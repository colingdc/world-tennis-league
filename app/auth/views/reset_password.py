from flask import render_template
from flask_login import current_user, login_user

from .. import bp
from ..forms import PasswordResetForm
from ..lib import get_user_by_email
from ...navigation import go_to_homepage
from ...notifications import display_success_message, display_error_message


@bp.route("/reset/<token>", methods=["GET", "POST"])
def reset_password(token):
    if not current_user.is_anonymous():
        return go_to_homepage()

    form = PasswordResetForm()

    if form.validate_on_submit():
        user = get_user_by_email(form.email.data)

        if user is None:
            display_error_message("L'adresse email entrée ne correspond pas au lien de "
                                  "réinitialisation envoyé.")

            return render_password_reset_page(form, token)

        if user.reset_password(token, form.password.data):
            display_success_message("Ton mot de passe a été mis à jour.")

            login_user(user)

            return go_to_homepage()
        else:
            display_error_message("L'adresse email entrée ne correspond pas au lien de "
                                  "réinitialisation envoyé.")

            return render_password_reset_page(form, token)

    return render_password_reset_page(form, token)


def render_password_reset_page(form, token):
    return render_template(
        "auth/reset_password.html",
        title="Réinitialisation du mot de passe",
        form=form,
        token=token
    )
