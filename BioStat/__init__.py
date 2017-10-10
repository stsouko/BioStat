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


def init():
    from datetime import datetime
    from flask import Flask
    from flask_bootstrap import Bootstrap
    from flask_nav import Nav, register_renderer
    from pathlib import PurePosixPath
    from .bootstrap import top_nav, CustomBootstrapRenderer
    from .config import PORTAL_NON_ROOT, SECRET_KEY, DEBUG, LAB_NAME, MAX_UPLOAD_SIZE, YANDEX_METRIKA
    from .views import view_bp

    app = Flask(__name__)

    app.config['DEBUG'] = DEBUG
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['BOOTSTRAP_SERVE_LOCAL'] = DEBUG
    app.config['ERROR_404_HELP'] = False
    app.config['MAX_CONTENT_LENGTH'] = MAX_UPLOAD_SIZE

    app.jinja_env.globals.update(year=datetime.utcnow, laboratory=LAB_NAME, yandex=YANDEX_METRIKA)

    register_renderer(app, 'myrenderer', CustomBootstrapRenderer)
    nav = Nav(app)
    nav.register_element('top_nav', top_nav)
    Bootstrap(app)

    app_url = PurePosixPath('/') / (PORTAL_NON_ROOT or '')
    app.register_blueprint(view_bp, url_prefix=app_url.as_posix() if PORTAL_NON_ROOT else None)

    return app
