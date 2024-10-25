from flask import redirect, render_template, request, url_for
from flask_login import current_user

from .. import bp
from ..forms import PasswordResetRequestForm
from ..lib import get_user_by_email
from ...email import send_email
from ...navigation import go_to_homepage
from ...notifications import display_info_message
from ...wordings import wordings


@bp.route("/reset", methods=["GET", "POST"])
def reset_password_request():
    if not current_user.is_anonymous():
        return go_to_homepage()

    form = PasswordResetRequestForm()

    if form.validate_on_submit():
        user = get_user_by_email(form.email.data)

        if user:
            token = user.generate_reset_token()

            send_email(
                user.email,
                wordings["password_reset"],
                "email/reset_password",
                user=user,
                token=token,
                next=request.args.get("next")
            )

        display_info_message(wordings["password_reset_email_sent"])

        return redirect(url_for("auth.login"))

    return render_template(
        "auth/reset_password_request.html",
        title=wordings["password_reset"],
        form=form
    )
