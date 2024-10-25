from flask import redirect, render_template, url_for
from flask_login import current_user, login_user

from .. import bp
from ..forms import PasswordResetForm
from ..lib import get_user_by_email
from ...notifications import display_success_message, display_error_message
from ...wordings import wordings


@bp.route("/reset/<token>", methods=["GET", "POST"])
def reset_password(token):
    if not current_user.is_anonymous():
        return redirect(url_for("main.index"))

    form = PasswordResetForm()

    if form.validate_on_submit():
        user = get_user_by_email(form.email.data)

        if user is None:
            display_error_message(wordings["invalid_reset_password_link"])

            return render_password_reset_page(form, token)

        if user.reset_password(token, form.password.data):
            display_success_message(wordings["password_updated"])

            login_user(user)

            return redirect(url_for("main.index"))
        else:
            display_error_message(wordings["invalid_reset_password_link"])

            return render_password_reset_page(form, token)

    return render_password_reset_page(form, token)


def render_password_reset_page(form, token):
    return render_template(
        "auth/reset_password.html",
        title=wordings["password_reset"],
        form=form,
        token=token
    )
