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
from collections import OrderedDict
from flask import url_for, redirect
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import SubmitField, HiddenField, BooleanField, SelectField, SelectMultipleField, StringField
from wtforms.validators import DataRequired
from .redirect import get_redirect_target, is_safe_url


class CustomForm(FlaskForm):
    next = HiddenField()
    _order = None

    @staticmethod
    def reorder(order, prefix=None):
        return ['%s-%s' % (prefix, x) for x in order] if prefix else list(order)

    def __iter__(self):
        collect = OrderedDict((x.name, x) for x in super(CustomForm, self).__iter__())
        for name in self._order or collect:
            yield collect[name]

    def __init__(self, *args, **kwargs):
        super(CustomForm, self).__init__(*args, **kwargs)
        if not self.next.data:
            self.next.data = get_redirect_target()

    def redirect(self, endpoint='.index', **values):
        if self.next.data and is_safe_url(self.next.data):
            return redirect(self.next.data)

        return redirect(url_for(endpoint, **values))


class Upload(CustomForm):
    sep = StringField('Separator', default=';', validators=[DataRequired()])
    nan = StringField('NaN keys')
    data = FileField('Data', validators=[DataRequired(), FileAllowed('csv '.split(), 'Table data only')])
    submit_btn = SubmitField('Upload')

    @property
    def nan_list(self):
        if self.nan.data:
            return self.nan.data.split(self.sep.data)
        return []


class Prepare(CustomForm):
    group = SelectMultipleField('Group', validators=[DataRequired()])
    data = SelectField('Data', validators=[DataRequired()])
    submit_btn = SubmitField('Prepare')

    def __init__(self, columns, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data.choices = self.group.choices = [(x, x) for x in columns]


class Download(CustomForm):
    delete = BooleanField('Delete data?')
    submit_btn = SubmitField('Download')
