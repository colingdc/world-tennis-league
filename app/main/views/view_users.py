from flask import render_template

from .. import bp
from ...decorators import manager_required
from ...models import User


@bp.route("/user/view")
@manager_required
def view_users():
    users = User.query.order_by(User.username)

    return render_template(
        "main/view_users.html",
        title="Utilisateurs",
        users=users
    )
