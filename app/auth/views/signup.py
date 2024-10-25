from flask import current_app, redirect, render_template, request, session, url_for
from flask_login import login_user, logout_user

from .. import bp
from ..forms import SignupForm
from ..lib import get_user_by_username, get_user_by_email, create_user
from ...email import send_email
from ...notifications import display_info_message


@bp.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm(request.form)

    if form.validate_on_submit():
        user_exists = get_user_by_username(form.username.data) is not None
        email_exists = get_user_by_email(form.email.data) is not None

        if user_exists:
            form.username.errors.append("Ce nom d'utilisateur est déjà pris")

        if email_exists:
            form.email.errors.append("Cet email existe déjà")

        if user_exists or email_exists:
            return render_signup_page(form)
        else:
            user = create_user(form.username.data, form.email.data, form.password.data)

            token = user.generate_confirmation_token()

            send_email(
                to=user.email,
                subject="Confirmation de ton adresse mail",
                template="email/confirm",
                user=user,
                token=token
            )

            send_email(
                to=current_app.config.get("ADMIN_WTL"),
                subject="Nouvel inscrit",
                template="email/new_user",
                user=user
            )

            display_info_message("Un email de confirmation t'a été envoyé.")

            session.pop("signed", None)
            session.pop("username", None)
            logout_user()
            login_user(user)

            return redirect(url_for("auth.unconfirmed"))
    else:
        return render_signup_page(form)


def render_signup_page(form):
    return render_template(
        "auth/signup.html",
        title="Inscription",
        form=form
    )
