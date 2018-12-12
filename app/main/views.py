from flask import render_template
from flask_login import current_user

from . import bp


@bp.route("/")
def index():
    if current_user.is_authenticated:
        return render_template("main/dashboard.html",
                               user=current_user)
    return render_template("main/index.html")
