from flask import redirect, url_for
from flask_login import current_user

from .. import bp
from ...decorators import auth_required
from ...navigation import go_to_homepage
from ...notifications import display_success_message, display_danger_message
from ...wordings import wordings


@bp.route("/confirm/<token>")
@auth_required
def confirm(token):
    if current_user.confirmed:
        return go_to_homepage()

    if current_user.confirm(token):
        display_success_message(wordings["account_validated"])
        return go_to_homepage()
    else:
        display_danger_message(wordings["invalid_confirmation_link"])
        return redirect(url_for("auth.unconfirmed"))
