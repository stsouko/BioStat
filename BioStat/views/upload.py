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
from flask import redirect, url_for, render_template, flash
from flask.views import View
from pandas import read_csv
from uuid import uuid4
from ..config import LAB_NAME, UPLOAD_ROOT
from ..forms import Upload


class UploadView(View):
    methods = ['GET', 'POST']

    def dispatch_request(self):
        tabs = [dict(title='Upload', glyph='arrow-up', active=True, url='#'),
                dict(title='Prepare', glyph='pencil', active=False, url='#'),
                dict(title='Results', glyph='stats', active=False, url='#')]

        active_form = Upload()
        if active_form.validate_on_submit():
            file_name = str(uuid4())
            sep = active_form.sep.data
            try:
                data = read_csv(active_form.data.data.stream, sep=sep, na_values=active_form.nan_list,
                                decimal=active_form.decimal.data)
                data.to_csv((UPLOAD_ROOT / file_name).as_posix(), index=False)
                return redirect(url_for('.prepare', data=file_name))
            except:
                flash('Data file is invalid')

        return render_template('forms.html', title=LAB_NAME, tabs=tabs, form=active_form, message='Data Upload')
