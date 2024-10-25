from flask import redirect, url_for
from flask_login import current_user

from .. import bp
from ...decorators import auth_required
from ...navigation import go_to_homepage
from ...notifications import display_success_message, display_danger_message


@bp.route("/confirm/<token>")
@auth_required
def confirm(token):
    if current_user.confirmed:
        return go_to_homepage()

    if current_user.confirm(token):
        display_success_message("Ton compte est à présent validé.")
        return go_to_homepage()
    else:
        display_danger_message("Ce lien de confirmation est invalide ou a expiré.")
        return redirect(url_for("auth.unconfirmed"))
