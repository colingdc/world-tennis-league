from flask import current_app, render_template, request, session
from flask_login import login_user, logout_user

from .. import bp
from ..forms import SignupForm
from ..lib import get_user_by_username, get_user_by_email, create_user
from ...email import send_email
from ...navigation import go_to_account_unconfirmed_page
from ...notifications import display_info_message
from ...wordings import wordings


@bp.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm(request.form)

    if form.validate_on_submit():
        user_exists = get_user_by_username(form.username.data) is not None
        email_exists = get_user_by_email(form.email.data) is not None

        if user_exists:
            form.username.errors.append(wordings["username_already_used"])

        if email_exists:
            form.email.errors.append(wordings["email_already_used"])

        if user_exists or email_exists:
            return render_signup_page(form)
        else:
            user = create_user(form.username.data, form.email.data, form.password.data)

            token = user.generate_confirmation_token()

            send_email(
                to=user.email,
                subject=wordings["email_address_confirmation"],
                template="email/confirm",
                user=user,
                token=token
            )

            send_email(
                to=current_app.config.get("ADMIN_WTL"),
                subject=wordings["new_user_signup"],
                template="email/new_user",
                user=user
            )

            display_info_message(wordings["confirmation_email_sent"])

            session.pop("signed", None)
            session.pop("username", None)
            logout_user()
            login_user(user)

            return go_to_account_unconfirmed_page()
    else:
        return render_signup_page(form)


def render_signup_page(form):
    return render_template(
        "auth/signup.html",
        title=wordings["signup"],
        form=form
    )
