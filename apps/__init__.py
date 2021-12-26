# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from importlib import import_module

from tinydb import TinyDB, Query

from woocommerce import API

from requests_oauthlib import OAuth1Session


wcapi = API(
    url="http://127.0.0.1/wordpress",
    consumer_key="ck_027591d5835d8e1636c8a985fefe4a8e445bb543",
    consumer_secret="cs_28cf43a659e02df4d047504ee81727745fc649e3",
    version="wc/v3"
)

wc_oauth = OAuth1Session('ck_027591d5835d8e1636c8a985fefe4a8e445bb543',
                    client_secret='cs_28cf43a659e02df4d047504ee81727745fc649e3')

tiny_db = TinyDB('db.json')
orders = tiny_db.table('orders')


db = SQLAlchemy()
login_manager = LoginManager()


def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)


def register_blueprints(app):
    for module_name in ('authentication', 'home'):
        module = import_module('apps.{}.routes'.format(module_name))
        app.register_blueprint(module.blueprint)


def configure_database(app):

    @app.before_first_request
    def initialize_database():
        db.create_all()

    @app.teardown_request
    def shutdown_session(exception=None):
        db.session.remove()


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    register_extensions(app)
    register_blueprints(app)
    configure_database(app)
    return app
