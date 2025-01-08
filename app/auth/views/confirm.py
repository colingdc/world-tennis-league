from flask import redirect, url_for
from flask_login import current_user

from .. import bp
from ...decorators import auth_required
from ...notifications import display_success_message, display_danger_message


@bp.route("/confirm/<token>")
@auth_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for("main.index"))

    if current_user.confirm(token):
        display_success_message("Ton compte est à présent validé.")
        return redirect(url_for("main.index"))
    else:
        display_danger_message("Ce lien de confirmation est invalide ou a expiré.")
        return redirect(url_for("auth.unconfirmed"))
