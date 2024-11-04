from flask_babel import _
from flask_login import current_user

from .. import bp
from ...decorators import auth_required
from ...navigation import go_to_homepage, go_to_account_unconfirmed_page
from ...notifications import display_success_message, display_danger_message


@bp.route("/confirm/<token>")
@auth_required
def confirm(token):
    if current_user.confirmed:
        return go_to_homepage()

    if current_user.confirm(token):
        display_success_message(_("account_validated"))
        return go_to_homepage()
    else:
        display_danger_message(_("invalid_confirmation_link"))
        return go_to_account_unconfirmed_page()
