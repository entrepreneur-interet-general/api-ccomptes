#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from os.path import exists, join


class DefaultConfig(object):
    MONGODB_DB = 'ccomptes'
    SECRET_KEY = 'no-secret-this-is-open'
    MAIL_DEFAULT_SENDER = 'ccomptes@locahost'
    ANON_ALERT_MAIL = 'ccomptes.alert@locahost'


def create_app(config=None):
    from flask import Flask

    from ccomptes import views, api
    from ccomptes.assets import assets
    from ccomptes.models import db
    from ccomptes.search import es

    app = Flask('ccomptes')

    app.config.from_object(DefaultConfig)
    app.config.from_envvar('CCOMPTES_CONFIG', silent=True)

    custom_settings = join(os.getcwd(), 'ccomptes.cfg')
    if exists(custom_settings):
        app.config.from_pyfile(custom_settings)

    if config:
        app.config.from_object(config)

    # Optionnal Sentry support
    if 'SENTRY_DSN' in app.config:
        from raven.contrib.flask import Sentry
        Sentry(app)

    db.init_app(app)
    es.init_app(app)
    assets.init_app(app)
    views.init_app(app)
    api.init_app(app)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run()
