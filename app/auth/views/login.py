from flask import redirect, render_template, session, url_for
from flask_login import current_user, login_user

from .. import bp
from ..forms import LoginForm
from ..lib import get_user_by_username
from ...notifications import display_success_message
from ...wordings import wordings


@bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    # Redirect user to homepage if they are already authenticated
    if current_user is not None and current_user.is_authenticated:
        return redirect(url_for("main.index"))

    # If form was submitted via a POST request
    if form.validate_on_submit():
        user = get_user_by_username(form.username.data)

        # If the credentials are incorrect, render the login page
        # with an error message
        if user is None:
            form.username.errors.append(wordings["invalid_credentials"])
            form.password.errors.append("")

            return render_login_page(form)

        is_password_correct = user.verify_password(form.password.data)
        if not is_password_correct:
            form.username.errors.append(wordings["invalid_credentials"])
            form.password.errors.append("")

            return render_login_page(form)

        # Otherwise log the user in
        login_user(user, remember=form.remember_me.data)
        session["signed"] = True
        session["username"] = user.username

        display_success_message(wordings["login_confirmed"])
        return redirect(url_for("auth.unconfirmed"))

    return render_login_page(form)


def render_login_page(form):
    return render_template(
        "auth/login.html",
        title=wordings["login"],
        form=form
    )
