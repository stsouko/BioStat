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
from pandas import read_csv, DataFrame
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
            df = read_csv(data_path.as_posix())
            paired, unpaired = defaultdict(dict), defaultdict(dict)

            gi = [active_form.date.data] + active_form.group.data
            mms = df.groupby(gi).agg(['mean', 'median', 'std'])
            for (d, *g), v in df.groupby(gi):
                g = tuple(g)
                v.set_index(gi, inplace=True)
                paired[g][d] = unpaired[d][g] = v  # .dropna()

            group_p = {}
            for k, v in paired.items():
                group_p[k] = day_p = {}
                for x, y in combinations(v, 2):
                    day_p[(x, y)] = data_p = {}
                    for g in active_form.data.data:
                        _, p_value = wilcoxon(v[x][g], v[y][g], zero_method='wilcox', correction=True)
                        data_p[g] = p_value

            paired = DataFrame({tuple(chain(i, m)): n for i, j in group_p.items() for m, n in j.items()}).T
            paired.index.names = active_form.group.data + ['Day_1', 'Day_2']

            day_u = {}
            for k, v in unpaired.items():
                day_u[k] = group_u = {}
                for x, y in combinations(v, 2):
                    group_u[(x, y)] = data_u = {}
                    for g in active_form.data.data:
                        _, p_value = mannwhitneyu(v[x][g], v[y][g], use_continuity=True)
                        data_u[g] = p_value
            unpaired = DataFrame({tuple(chain((i,), *m)): n for i, j in day_u.items() for m, n in j.items()}).T
            unpaired.index.names = ['Day'] + ['%s_%d' % (y, x) for x in (1, 2) for y in active_form.group.data]

            print(paired)
            print(unpaired)
            print(mms)

            with (RESULTS_ROOT / data).open('w'):
                pass

            return redirect(url_for('.download', data=data))

        return render_template('forms.html', title=LAB_NAME, tabs=tabs, form=active_form, message='Data Preparation')
