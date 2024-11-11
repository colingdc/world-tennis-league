import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

from flask import Flask, redirect, url_for
from flask_babel import Babel, format_datetime
from flask_bcrypt import Bcrypt
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

from config import config

babel = Babel()
db = SQLAlchemy()
bcrypt = Bcrypt()
bootstrap = Bootstrap()
login_manager = LoginManager()
mail = Mail()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config.get(config_name))
    app.url_map.strict_slashes = False
    CSRFProtect(app)

    babel.init_app(app)
    db.init_app(app)
    bootstrap.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    register_filters(app)
    register_loggers(app)
    register_datetime_filters(app)
    register_blueprints(app)
    register_favicon_route(app)
    register_error_handlers(app)

    return app


def register_filters(app):
    @app.template_filter("autoversion")
    def autoversion_filter(filename):
        fullpath = os.path.join("app/", filename[1:])
        try:
            timestamp = str(os.path.getmtime(fullpath))
        except OSError:
            return filename
        return f"{filename}?v={timestamp}"


def register_loggers(app):
    error_handler = RotatingFileHandler("logs/app.log", maxBytes=1000000, backupCount=1)
    formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
    error_handler.setFormatter(formatter)
    app.logger.addHandler(error_handler)


def register_datetime_filters(app):
    def custom_datetime_filter(value):
        dt = format_datetime(value, "EEEE d MMMM yyyy à H:mm")
        return dt.capitalize()

    def custom_datetime_difference_filter(value):
        interval = value - datetime.now()
        duration = interval.total_seconds()
        if duration < 0:
            return "imminente"
        minutes = int((duration // 60) % 60)
        hours = int((duration // 3600) % 24)
        days = int(duration // 86400)
        if days > 1:
            return f"dans {days} jours"
        if days == 1:
            if hours > 1:
                return f"dans 1 jour et {hours} heures"
            if hours == 1:
                return "dans 1 jour et 1 heure"
            return "dans 1 jour"
        if hours > 1:
            if minutes > 1:
                return f"dans {hours} heures et {minutes} minutes"
            if minutes == 1:
                return f"dans {hours} heures"
        if minutes > 1:
            return f"dans {minutes} minutes"
        return "dans moins de 2 minutes"

    app.jinja_env.filters["dt"] = custom_datetime_filter
    app.jinja_env.filters["dt_diff"] = custom_datetime_difference_filter


def register_blueprints(app):
    from .public import bp as public_blueprint
    app.register_blueprint(public_blueprint)

    from .auth import bp as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix="/wtl")

    from .main import bp as main_blueprint
    app.register_blueprint(main_blueprint, url_prefix="/wtl")

    from .tournament import bp as tournament_blueprint
    app.register_blueprint(tournament_blueprint, url_prefix="/wtl/tournament")

    from .user import bp as user_blueprint
    app.register_blueprint(user_blueprint, url_prefix="/wtl/user")

    from .ranking import bp as ranking_blueprint
    app.register_blueprint(ranking_blueprint, url_prefix="/wtl/ranking")

    from .player import bp as player_blueprint
    app.register_blueprint(player_blueprint, url_prefix="/wtl/player")


def register_favicon_route(app):
    @app.route("/favicon.ico")
    def favicon():
        return redirect(url_for("static", filename="images/logo.png"))


def register_error_handlers(app):
    from .errors import unauthorized, forbidden, page_not_found, bad_request, internal_server_error, unhandled_exception

    app.register_error_handler(401, unauthorized)
    app.register_error_handler(403, forbidden)
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(400, bad_request)
    app.register_error_handler(500, internal_server_error)
    # app.register_error_handler(Exception, unhandled_exception)
