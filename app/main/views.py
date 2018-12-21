from flask import render_template
from flask_login import current_user, login_required

from . import bp
from ..models import User


@bp.route("/")
def index():
    if current_user.is_authenticated:
        return render_template("main/dashboard.html",
                               user=current_user)
    return render_template("main/index.html")


@bp.route("/user/<user_id>")
@login_required
def view_user(user_id):
    user = User.query.get_or_404(user_id)
    title = f"Profil de {user.username}"

    return render_template("main/view_user.html",
                           title=title,
                           user=user)
