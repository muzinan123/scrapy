# -*- coding: utf-8 -*-
import os
import logging

from flask import Flask
from jinja2 import Markup
from flask_sqlalchemy import SQLAlchemy

import config


app = Flask(__name__)
db = SQLAlchemy(app)
# Flask-SQLAlchemy must be initialized before Flask-Marshmallow.
# ma = Marshmallow(app)


deploy_env = os.environ.get('DEPLOY_ENV', None)
if deploy_env == 'prd':
    app.config.from_object(config.ProductConfig)
elif deploy_env == 'pre':
    app.config.from_object(config.PreConfig)
elif deploy_env == 'test':
    app.config.from_object(config.TestingConfig)
else:
    app.config.from_object(config.DevelopConfig)

# logging config
FORMAT = '%(asctime)-15s [%(threadName)s] %(levelname)s [%(funcName)s] [%(lineno)d] -%(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)


from views import *
'''sqlite file不需要升级
import flask_migrate
if not app.config['DEBUG']:
    migrate = flask_migrate.Migrate(app, db)
    with app.app_context():
        flask_migrate.upgrade()
'''

def render_markup(snippet):
    return Markup(snippet)

app.jinja_env.globals['render_markup'] = render_markup


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
