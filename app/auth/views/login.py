from flask import render_template, session
from flask_babel import _
from flask_login import current_user, login_user

from .. import bp
from ..forms import LoginForm
from ..lib import get_user_by_username
from ...navigation import go_to_homepage, go_to_account_unconfirmed_page
from ...notifications import display_success_message


@bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if current_user is not None and current_user.is_authenticated:
        return go_to_homepage()

    if form.validate_on_submit():
        user = get_user_by_username(form.username.data)

        if user is None:
            form.username.errors.append(_("invalid_credentials"))
            form.password.errors.append("")

            return render_login_page(form)

        is_password_correct = user.verify_password(form.password.data)
        if not is_password_correct:
            form.username.errors.append(_("invalid_credentials"))
            form.password.errors.append("")

            return render_login_page(form)

        login_user(user, remember=form.remember_me.data)
        session["signed"] = True
        session["username"] = user.username

        display_success_message(_("login_confirmed"))
        return go_to_account_unconfirmed_page()

    return render_login_page(form)


def render_login_page(form):
    return render_template(
        "auth/login.html",
        title=_("login"),
        form=form
    )
