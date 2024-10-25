from flask import redirect, render_template, session, url_for
from flask_login import current_user, login_user

from .. import bp
from ..forms import LoginForm
from ...models import User
from ...notifications import display_success_message


@bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    # Redirect user to homepage if they are already authenticated
    if current_user is not None and current_user.is_authenticated:
        return redirect(url_for("main.index"))

    # If form was submitted via a POST request
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        # If the credentials are incorrect, render the login page
        # with an error message
        if user is None:
            form.username.errors.append("Identifiants incorrects")
            form.password.errors.append("")

            return render_template(
                "auth/login.html",
                title="Connexion",
                form=form
            )

        is_password_correct = user.verify_password(form.password.data)
        if not is_password_correct:
            form.username.errors.append("Identifiants incorrects")
            form.password.errors.append("")

            return render_template(
                "auth/login.html",
                title="Connexion",
                form=form
            )

        # Otherwise log the user in
        login_user(user, remember=form.remember_me.data)
        session["signed"] = True
        session["username"] = user.username

        display_success_message("Tu es à présent connecté.")
        return redirect(url_for("auth.unconfirmed"))

    return render_template(
        "auth/login.html",
        title="Connexion",
        form=form
    )
