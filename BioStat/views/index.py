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
from flask import redirect, url_for, render_template, make_response
from flask.views import View
from io import StringIO
from pandas import read_csv
from ..config import LAB_NAME
from ..constants import FormRoute
from ..forms import Upload


class IndexView(View):
    methods = ['GET', 'POST']

    def dispatch_request(self, action=1):
        form = FormRoute.get(action)
        if not form:
            return redirect(url_for('.index'))

        tabs = [dict(title='Wilcoxon', glyph='arrow-up', active=False,
                     url=url_for('.index', action=FormRoute.WILCOXON.value))]

        if form == FormRoute.WILCOXON:
            message = 'Wilcoxon Data Analysis'
            tabs[0]['active'] = True
            active_form = Upload()
            if active_form.validate_on_submit():
                data = read_csv(active_form.data.data.stream)
                resp = make_response(data.to_csv())
                resp.headers["Content-Disposition"] = "attachment; filename=result.csv"
                resp.headers["Content-Type"] = "text/csv"
                return resp

        return render_template("forms.html", title=LAB_NAME, tabs=tabs, form=active_form, message=message)
