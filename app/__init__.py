from flask import Flask
from flask_babel import Babel, format_datetime
from flask_bcrypt import Bcrypt
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
import os
from config import config
from datetime import datetime

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
        return User.query.filter(User.id == int(user_id)).first()

    @app.template_filter('autoversion')
    def autoversion_filter(filename):
        # determining fullpath might be project specific
        fullpath = os.path.join('app/', filename[1:])
        try:
            timestamp = str(os.path.getmtime(fullpath))
        except OSError:
            return filename
        newfilename = "{0}?v={1}".format(filename, timestamp)
        return newfilename

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

    from .public import bp as public_blueprint
    app.register_blueprint(public_blueprint)

    from .auth import bp as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix="/wtl")

    from .main import bp as main_blueprint
    app.register_blueprint(main_blueprint, url_prefix="/wtl")

    from .tournament import bp as tournament_blueprint
    app.register_blueprint(tournament_blueprint, url_prefix="/wtl/tournament")

    from .ranking import bp as ranking_blueprint
    app.register_blueprint(ranking_blueprint, url_prefix="/wtl/ranking")

    from .player import bp as player_blueprint
    app.register_blueprint(player_blueprint, url_prefix="/wtl/player")

    from .errors import (forbidden, page_not_found, bad_request,
                         internal_server_error, unhandled_exception)

    if not app.config["DEBUG"]:
        app.register_error_handler(401, forbidden)
        app.register_error_handler(403, forbidden)
        app.register_error_handler(404, page_not_found)
        app.register_error_handler(400, bad_request)
        app.register_error_handler(500, internal_server_error)
        app.register_error_handler(Exception, unhandled_exception)

    return app
