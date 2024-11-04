from flask import render_template
from flask_babel import _
from flask_login import current_user

from .. import bp
from ..forms import ChangePasswordForm
from ... import db
from ...decorators import login_required
from ...navigation import go_to_homepage
from ...notifications import display_success_message


@bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data

            db.session.add(current_user)

            display_success_message(_("password_updated"))
            return go_to_homepage()
        else:
            form.old_password.errors.append(_("invalid_password"))

    return render_template(
        "auth/change_password.html",
        title=_("password_change"),
        form=form,
        user=current_user
    )
