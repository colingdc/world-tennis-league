from flask import render_template

from .. import bp
from ...decorators import manager_required
from ...models import User
from ...wordings import wordings


@bp.route("/raw")
@manager_required
def view_users_raw():
    users = User.query.order_by(User.username)
    users = [user for user in users if not user.email.startswith("TEMPORARY")]

    return render_template(
        "main/view_users_raw.html",
        title=wordings["users"],
        users=users
    )
