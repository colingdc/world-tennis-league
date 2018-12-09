from flask import render_template, redirect, request, session, flash, url_for, current_app

from . import bp
from .forms import (LoginForm, SignupForm, ChangePasswordForm, PasswordResetForm, PasswordResetRequestForm)


@bp.route("/signup", methods = ["GET", "POST"])
def signup():
    title = "Inscription"
    form = SignupForm(request.form)

    if form.validate_on_submit():
        user_exist = User.query.filter_by(username = form.username.data).first()
        email_exist = User.query.filter_by(email = form.email.data).first()
        if user_exist:
            form.username.errors.append(USERNAME_ALREADY_TAKEN)
        if email_exist:
            form.email.errors.append(EMAIL_ALREADY_TAKEN)
        if user_exist or email_exist:
            return render_template("auth/signup.html", form = form, title = title)
        else:
            user = User(username = form.username.data,
                        email = form.email.data,
                        password = form.password.data)
            db.session.add(user)
            db.session.commit()
            token = user.generate_confirmation_token()
            send_email(user.email, "Confirmation de votre adresse mail",
                       "email/confirm", user = user, token = token)

            send_email(current_app.config.get("ADMIN_JDL"),
                       "Nouvel inscrit au jeu de L'orgue",
                       "email/new_user",
                       user = user)

            flash(CONFIRMATION_MAIL_SENT, "info")
            session.pop("signed", None)
            session.pop("username", None)
            logout_user()
            return redirect(url_for("auth.login"))
    else:
        return render_template("auth/signup.html", form = form, title = title)