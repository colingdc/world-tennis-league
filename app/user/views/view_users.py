from flask import render_template
from flask_babel import _

from .. import bp
from ...decorators import manager_required
from ...models import User


@bp.route("/view")
@manager_required
def view_users():
    users = User.query.order_by(User.username)

    return render_template(
        "main/view_users.html",
        title=_("users"),
        users=users
    )
