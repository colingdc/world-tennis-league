from flask import render_template, request
from flask_babel import _
from flask_login import current_user

from .. import bp
from ..forms import PasswordResetRequestForm
from ..lib import get_user_by_email
from ...email import send_email
from ...navigation import go_to_homepage, go_to_login_page
from ...notifications import display_info_message


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
                _("password_reset"),
                "email/reset_password",
                user=user,
                token=token,
                next=request.args.get("next")
            )

        display_info_message(_("password_reset_email_sent"))

        return go_to_login_page()

    return render_template(
        "auth/reset_password_request.html",
        title=_("password_reset"),
        form=form
    )
