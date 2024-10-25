from flask import redirect, url_for
from flask_login import current_user

from .. import bp
from ...decorators import auth_required
from ...notifications import display_success_message, display_danger_message
from ...wordings import wordings


@bp.route("/confirm/<token>")
@auth_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for("main.index"))

    if current_user.confirm(token):
        display_success_message(wordings["account_validated"])
        return redirect(url_for("main.index"))
    else:
        display_danger_message(wordings["invalid_confirmation_link"])
        return redirect(url_for("auth.unconfirmed"))
