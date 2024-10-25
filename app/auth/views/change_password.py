from flask import redirect, render_template, url_for
from flask_login import current_user

from .. import bp
from ..forms import ChangePasswordForm
from ... import db
from ...decorators import login_required
from ...notifications import display_success_message


@bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data

            db.session.add(current_user)

            display_success_message("Ton mot de passe a été mis à jour.")
            return redirect(url_for("main.index"))
        else:
            form.old_password.errors.append("Mot de passe incorrect")

    return render_template(
        "auth/change_password.html",
        title="Changement de mot de passe",
        form=form,
        user=current_user
    )
