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
from flask import Blueprint
from .index import IndexView

view_bp = Blueprint('view', __name__)


index_view = IndexView.as_view('index')
view_bp.add_url_rule('/', view_func=index_view)
view_bp.add_url_rule('/index', view_func=index_view)
view_bp.add_url_rule('/<int:action>', view_func=index_view)
view_bp.add_url_rule('/index/<int:action>', view_func=index_view)
