from flask import render_template

from .. import bp
from ...decorators import manager_required
from ...models import User


@bp.route("/user/raw")
@manager_required
def view_users_raw():
    users = User.query.order_by(User.username)
    users = [user for user in users if not user.email.startswith("TEMPORARY")]

    return render_template(
        "main/view_users_raw.html",
        title="Utilisateurs",
        users=users
    )
