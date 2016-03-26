import config
import logging, sys
import flask
import os

from flask import Flask, redirect
from flask.ext.bcrypt import Bcrypt
from flask.ext.cache import Cache
from flask.ext.login import LoginManager, login_required, current_user, login_user, logout_user
from flask.ext.migrate import Migrate
from flask.ext.principal import Principal, RoleNeed, UserNeed, Permission, \
    Identity, identity_loaded, identity_changed, AnonymousIdentity
from flask.ext.sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, send as sio_send, emit as sio_emit
from flask_bootstrap import Bootstrap
from psycopg2.extras import register_hstore


app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(sys.stderr))
app.logger.setLevel(logging.ERROR)
app.config.from_object('config')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')
app.jinja_env.pyjade.options['autocloseCode'] = ['assets']

admin_permission = Permission(RoleNeed('admin'))
manager_permission = Permission(RoleNeed('manager'))
gamer_permission = Permission(RoleNeed('gamer'))

socketio = SocketIO(app,
                    logger=True,
                    engineio_logger=True,
                    async_mode='eventlet',
                    max_size=32)
cache = Cache(app,config={'CACHE_TYPE': 'simple'})
bcrypt = Bcrypt(app)
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
lm = LoginManager(app)
migrate = Migrate(app, db)
principals = Principal(app)

@cache.memoize(3600)
def get_option(name):
    return models.Option.query.filter(models.Option.name == name).one().value


from app import models
from app import controllers

@lm.unauthorized_handler
def unauthorized():
    return redirect('login')

@lm.user_loader
def load_user(user_id):
    if user_id is None or user_id == 'None':
        return None
    elif user_id.startswith('g_'):
        return models.Gamer.query.filter(models.Gamer.id == user_id[2:]).one_or_none()
    else:
        return models.User.query.filter(models.User.id == user_id).one_or_none()

@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    identity.user = current_user
    if hasattr(current_user, 'id'):
        identity.provides.add(UserNeed(current_user.id))
    if hasattr(current_user, 'roles'):
        for role in current_user.roles:
            identity.provides.add(RoleNeed(role.name))

@app.errorhandler(404)
def any_error(error):
    return flask.render_template('404.jade', title='404 Not Found'), 404

@app.errorhandler(500)
def any_error(error):
    return flask.render_template('500.jade', title='500 Internal Error'), 500

@app.before_first_request
def enable_hstore():
    register_hstore(db.engine.raw_connection(), True)
