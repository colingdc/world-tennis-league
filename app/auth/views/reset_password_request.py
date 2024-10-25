from flask import redirect, render_template, request, url_for
from flask_login import current_user

from .. import bp
from ..forms import PasswordResetRequestForm
from ..lib import get_user_by_email
from ...email import send_email
from ...notifications import display_info_message


@bp.route("/reset", methods=["GET", "POST"])
def reset_password_request():
    if not current_user.is_anonymous():
        return redirect(url_for("main.index"))

    form = PasswordResetRequestForm()

    if form.validate_on_submit():
        user = get_user_by_email(form.email.data)

        if user:
            token = user.generate_reset_token()

            send_email(
                user.email,
                "Réinitialisation du mot de passe",
                "email/reset_password",
                user=user,
                token=token,
                next=request.args.get("next")
            )

        display_info_message("Un email contenant des instructions pour réinitialiser "
                             "ton mot de passe t'a été envoyé. Si tu n'as pas reçu d'email, "
                             "vérifie dans ton dossier de spams et assure toi d'avoir rentré "
                             "la bonne adresse mail.")

        return redirect(url_for("auth.login"))

    return render_template(
        "auth/reset_password_request.html",
        title="Réinitialisation du mot de passe",
        form=form
    )
