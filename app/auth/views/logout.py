from flask import session
from flask_login import logout_user

from .. import bp
from ...navigation import go_to_homepage


@bp.route("/logout")
def logout():
    session.pop("signed", None)
    session.pop("username", None)
    logout_user()

    return go_to_homepage()
