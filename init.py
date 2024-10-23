# encoding: utf-8
from flask import Flask
import os
from settings import config, BaseConfig
from extensions import cors, mongo
from views import triplet_bp

def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')
    app = Flask(__name__, template_folder='page', static_folder="", static_url_path="")
    app.config.from_object(config[config_name])
    app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024
    register_extensions(app)
    register_blueprints(app)
    return app


def register_extensions(app):
    mongo.init_app(app)
    # cors.init_app(app, supports_credentials=True)  # 解决跨域问题  #注意和前端一起使用 'application/json;charset=utf-8'
    # cors.init_app(app, resources={r"/*": {"origins":"*"}}, send_wildcard=True)


def register_blueprints(app):
    app.register_blueprint(triplet_bp)
