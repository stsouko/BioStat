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
from werkzeug.utils import secure_filename
from ..config import LAB_NAME, UPLOAD_ROOT, RESULTS_ROOT
from ..forms import Download


class DownloadView(View):
    methods = ['GET', 'POST']

    def dispatch_request(self, data):
        data = secure_filename(data)
        data_path = (RESULTS_ROOT / data)
        if not data_path.exists():
            return redirect(url_for('.index'))

        tabs = [dict(title='Upload', glyph='arrow-up', active=False, url=url_for('.index')),
                dict(title='Prepare', glyph='pencil', active=False, url=url_for('.prepare', data=data)),
                dict(title='Results', glyph='stats', active=True, url='#')]

        active_form = Download()
        if active_form.validate_on_submit():
            resp = make_response(data_path.open().read())
            resp.headers['Content-Disposition'] = 'attachment; filename=result.csv'
            resp.headers['Content-Type'] = 'text/csv'

            if active_form.delete.data:
                data_path.unlink()
                (UPLOAD_ROOT / data).unlink()

            return resp

        return render_template('forms.html', title=LAB_NAME, tabs=tabs, form=active_form, message='Analysis Results')
