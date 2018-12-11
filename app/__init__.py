from flask import Flask
from flask_bcrypt import Bcrypt
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
import os
from config import config

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

    from .auth import bp as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .main import bp as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
