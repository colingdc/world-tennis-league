from flask_login import current_user

from .. import bp
from ...decorators import auth_required
from ...email import send_email
from ...navigation import go_to_account_unconfirmed_page
from ...notifications import display_info_message


@bp.route("/confirm")
@auth_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()

    send_email(
        to=current_user.email,
        subject="Confirmation de ton adresse mail",
        template="email/confirm",
        user=current_user,
        token=token
    )

    display_info_message("Un email de confirmation t'a été envoyé.")
    return go_to_account_unconfirmed_page()
