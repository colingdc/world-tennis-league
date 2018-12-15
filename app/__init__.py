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

    app.jinja_env.filters["dt"] = custom_datetime_filter

    from .auth import bp as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .main import bp as main_blueprint
    app.register_blueprint(main_blueprint)

    from .tournament import bp as tournament_blueprint
    app.register_blueprint(tournament_blueprint, url_prefix="/tournament")

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
