from flask import Flask
from flask_wtf.csrf import CSRFProtect

from config import config

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config.get(config_name))
    app.url_map.strict_slashes = False
    CSRFProtect(app)

    @app.route("/")
    def index():
        return "hello"

    return app
