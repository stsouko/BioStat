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
from itertools import combinations
from pandas import read_csv, DataFrame, MultiIndex, merge, concat
from scipy.stats import wilcoxon, mannwhitneyu
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

            df = read_csv(data_path.as_posix(), usecols=gi + data_fields)
            mms = df.groupby(gi).agg(['mean', 'median', 'std']).reset_index()
            mms.columns = mms.columns.swaplevel()

            paired, unpaired = defaultdict(dict), defaultdict(dict)
            for (d, *g), v in df.groupby(gi):
                g = tuple(g)
                v.set_index(gi, inplace=True)
                paired[g][d] = unpaired[d][g] = v  # .dropna()

            group_p = []
            for g, dv in paired.items():
                for x, y in combinations(dv, 2):
                    tmp = {'%s_1' % date_field: x, '%s_2' % date_field: y}
                    tmp.update(zip(group_fields, g))
                    group_p.append(tmp)
                    for f in data_fields:
                        _, p_value = wilcoxon(dv[x][f], dv[y][f], zero_method='wilcox', correction=True)
                        tmp[f] = p_value
            paired = DataFrame(group_p)
            paired.columns = MultiIndex.from_tuples([('p_value', x) if x in data_fields else ('', x)
                                                     for x in paired.columns])

            group_u = []
            for d, gv in unpaired.items():
                for x, y in combinations(gv, 2):
                    tmp = {date_field: d}
                    tmp.update(zip(('%s_%d' % (y, x) for x in (1, 2) for y in group_fields), x + y))
                    group_u.append(tmp)
                    for f in data_fields:
                        _, p_value = mannwhitneyu(gv[x][f], gv[y][f], use_continuity=True)
                        tmp[f] = p_value
            unpaired = DataFrame(group_u)
            unpaired.columns = MultiIndex.from_tuples([('p_value', x) if x in data_fields else ('', x)
                                                       for x in unpaired.columns])

            rgi = [('', x) for x in gi]
            rgf = [('', x) for x in group_fields]

            tmp = merge(mms, paired, left_on=rgi, right_on=[('', '%s_1' % date_field)] + rgf)
            tmp.pop(('', date_field))
            paired_mms = merge(mms, tmp, left_on=rgi, right_on=[('', '%s_2' % date_field)] + rgf, suffixes=('_2', '_1'))
            paired_mms.pop(('', date_field))
            for x in group_fields:
                paired_mms[('', '%s_1' % x)] = paired_mms[('', '%s_2' % x)] = paired_mms.pop(('', x))

            tmp = merge(mms, unpaired, left_on=rgi,
                        right_on=[('', date_field)] + [('', '%s_1' % x) for x in group_fields])
            for x in rgf:
                tmp.pop(x)
            unpaired_mms = merge(mms, tmp, left_on=rgi, suffixes=('_2', '_1'),
                                 right_on=[('', date_field)] + [('', '%s_2' % x) for x in group_fields])
            for x in rgf:
                unpaired_mms.pop(x)
            unpaired_mms[('', '%s_1' % date_field)] = unpaired_mms[('', '%s_2' % date_field)] = \
                unpaired_mms.pop(('', date_field))

            paired_mms[('', 'Type')] = 'paired'
            unpaired_mms[('', 'Type')] = 'unpaired'
            paired_mms.columns = paired_mms.columns.swaplevel()
            unpaired_mms.columns = unpaired_mms.columns.swaplevel()

            paired_mms = DataFrame(paired_mms.to_dict())
            unpaired_mms = DataFrame(unpaired_mms.to_dict())

            with (RESULTS_ROOT / data).open('w') as f:
                concat([paired_mms, unpaired_mms]).to_csv(f)

            return redirect(url_for('.download', data=data))

        return render_template('forms.html', title=LAB_NAME, tabs=tabs, form=active_form, message='Data Preparation')
