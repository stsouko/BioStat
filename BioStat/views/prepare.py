# -*- coding: utf-8 -*-
#
#  Copyright 2017 Ramil Nugmanov <stsouko@live.ru>
#  This file is part of BioStat.
#
#  BioStat
#  is free software; you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
from collections import defaultdict
from flask import url_for, render_template, redirect
from flask.views import View
from itertools import combinations, chain
from pandas import read_csv, DataFrame, MultiIndex, merge, concat
from scipy.stats import wilcoxon, mannwhitneyu
from statsmodels.sandbox.stats.multicomp import multipletests
from werkzeug.utils import secure_filename
from ..config import LAB_NAME, UPLOAD_ROOT, RESULTS_ROOT
from ..forms import Prepare


class PrepareView(View):
    methods = ['GET', 'POST']

    def dispatch_request(self, data):
        data = secure_filename(data)
        data_path = (UPLOAD_ROOT / data)
        if not data_path.exists():
            return redirect(url_for('.index'))

        tabs = [dict(title='Upload', glyph='arrow-up', active=False, url=url_for('.index')),
                dict(title='Prepare', glyph='pencil', active=True, url='#'),
                dict(title='Results', glyph='stats', active=False, url='#')]

        header = list(read_csv(data_path.as_posix(), nrows=1).columns)
        active_form = Prepare(header)
        if active_form.validate_on_submit():
            data_fields = active_form.data.data
            group_fields = active_form.group.data
            date_field = active_form.date.data
            gi = [date_field] + group_fields

            rgi = [('', x) for x in gi]
            rgi_1 = [('', '%s_1' % x) for x in gi]
            rgi_2 = [('', '%s_2' % x) for x in gi]

            df = read_csv(data_path.as_posix(), usecols=gi + data_fields)
            mms = df.groupby(gi).agg(['mean', 'median', 'std']).reset_index()
            mms.columns = mms.columns.swaplevel()

            paired, unpaired = defaultdict(dict), defaultdict(dict)
            for (d, *g), v in df.groupby(gi):
                g = tuple(g)
                v.set_index(gi, inplace=True)
                paired[g][d] = unpaired[d][g] = v

            group_u = []

            if len(unpaired) > 1:
                group_p = []
                for g, dv in paired.items():
                    dgf = dict(zip(('%s_%d' % (y, x) for x in (1, 2) for y in group_fields), g * 2))
                    for x, y in combinations(dv, 2):
                        tmp1 = {}
                        tmp2 = {}

                        for f in data_fields:
                            vxf, vyf = dv[x][f], dv[y][f]
                            loc = ~(vxf.isnull().as_matrix() | vyf.isnull().as_matrix())
                            if loc.mean() > .0001:
                                _, p_value = wilcoxon(vxf.loc[loc], vyf.loc[loc], zero_method='wilcox', correction=True)
                                tmp1[f] = p_value
                            else:
                                try:
                                    _, p_value = mannwhitneyu(vxf.dropna(), vyf.dropna(), use_continuity=True)
                                except ValueError:
                                    p_value = .5
                                tmp2[f] = p_value * 2
                        if tmp1:
                            tmp1.update(dgf)
                            tmp1.update({'%s_1' % date_field: x, '%s_2' % date_field: y, 'Type': 'Paired Wilcoxon'})
                            group_p.append(tmp1)
                        if tmp2:
                            tmp2.update(dgf)
                            tmp2.update({'%s_1' % date_field: x, '%s_2' % date_field: y, 'Type': 'Unpaired Wilcoxon'})
                            group_u.append(tmp2)

                paired = DataFrame(group_p)
                paired.columns = MultiIndex.from_tuples([('p-value', x) if x in data_fields else ('', x)
                                                         for x in paired.columns])
                for x in data_fields:
                    reject, p_value_adj, *_ = multipletests(paired[('p-value', x)], alpha=0.05, method='fdr_bh',
                                                            is_sorted=False, returnsorted=False)
                    paired[('p-value_adj', x)] = p_value_adj
                    paired[('significance', x)] = reject

                tmp = merge(mms, paired, left_on=rgi, right_on=rgi_1)
                for x in rgi:
                    tmp.pop(x)
                paired_mms = merge(mms, tmp, left_on=rgi, right_on=rgi_2, suffixes=('_2', '_1'))
                for x in rgi:
                    paired_mms.pop(x)

                paired_mms.columns = paired_mms.columns.swaplevel()
                paired_mms = DataFrame(paired_mms.to_dict())
            else:
                paired_mms = DataFrame()

            for d, gv in unpaired.items():
                dfd = {'%s_1' % date_field: d, '%s_2' % date_field: d, 'Type': 'Unpaired Wilcoxon'}
                for x, y in combinations(gv, 2):
                    tmp = dict(zip(('%s_%d' % (y, x) for x in (1, 2) for y in group_fields), x + y))
                    tmp.update(dfd)
                    group_u.append(tmp)
                    for f in data_fields:
                        try:
                            _, p_value = mannwhitneyu(gv[x][f].dropna(), gv[y][f].dropna(), use_continuity=True)
                        except ValueError:
                            p_value = .5
                        tmp[f] = p_value * 2

            unpaired = DataFrame(group_u)
            unpaired.columns = MultiIndex.from_tuples([('p-value', x) if x in data_fields else ('', x)
                                                       for x in unpaired.columns])
            for d, g in unpaired.groupby([('', '%s_1' % date_field)]):
                for x in data_fields:
                    reject, p_value_adj, *_ = multipletests(g[('p-value', x)], alpha=0.05, method='fdr_bh',
                                                            is_sorted=False, returnsorted=False)
                    unpaired.loc[unpaired[('', '%s_1' % date_field)] == d, ('p-value_adj', x)] = p_value_adj
                    unpaired.loc[unpaired[('', '%s_1' % date_field)] == d, ('significance', x)] = reject

            tmp = merge(mms, unpaired, left_on=rgi, right_on=rgi_1)
            for x in rgi:
                tmp.pop(x)
            unpaired_mms = merge(mms, tmp, left_on=rgi, right_on=rgi_2, suffixes=('_2', '_1'))
            for x in rgi:
                unpaired_mms.pop(x)

            unpaired_mms.columns = unpaired_mms.columns.swaplevel()
            unpaired_mms = DataFrame(unpaired_mms.to_dict())

            result = concat([paired_mms, unpaired_mms])
            result.index = range(len(result.index))
            result = result[list(chain((('%s_%d' % (y, x), '') for x in (1, 2) for y in gi), (('Type', ''), ),
                                       ((x, y) for x in data_fields for y in
                                        chain(('%s_%d' % (y, x) for x in (1, 2) for y in ('median', 'mean', 'std')),
                                              ('p-value', 'p-value_adj', 'significance')))))]

            result.to_excel((RESULTS_ROOT / data).as_posix(), engine='openpyxl')

            return redirect(url_for('.download', data=data))

        return render_template('forms.html', title=LAB_NAME, tabs=tabs, form=active_form, message='Data Preparation')
