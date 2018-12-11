from flask import (current_app, flash, redirect, render_template, request,
                   session, url_for)
from flask_login import current_user, login_user, logout_user, login_required

from . import bp
from .. import db
from ..email import send_email
from ..models import User
from .forms import LoginForm, SignupForm


@bp.route("/signup", methods=["GET", "POST"])
def signup():
    title = "Inscription"
    form = SignupForm(request.form)

    if form.validate_on_submit():
        user_exists = User.query.filter_by(username=form.username.data).first()
        email_exists = User.query.filter_by(email=form.email.data).first()
        if user_exists:
            form.username.errors.append("Ce nom d'utilisateur est déjà pris")
        if email_exists:
            form.email.errors.append("Cet email existe déjà")
        if user_exists or email_exists:
            return render_template("auth/signup.html",
                                   form=form,
                                   title=title)
        else:
            user = User(username=form.username.data,
                        email=form.email.data,
                        password=form.password.data)
            db.session.add(user)
            db.session.commit()
            token = user.generate_confirmation_token()
            send_email(to=user.email,
                       subject="Confirmation de votre adresse mail",
                       template="email/confirm",
                       user=user,
                       token=token)

            send_email(to=current_app.config.get("ADMIN_WTL"),
                       subject="Nouvel inscrit",
                       template="email/new_user",
                       user=user)

            flash("Email de confirmation envoyé", "info")
            session.pop("signed", None)
            session.pop("username", None)
            logout_user()
            login_user(user)
            return redirect(url_for("auth.unconfirmed"))
    else:
        return render_template("auth/signup.html",
                               form=form,
                               title=title)


@bp.route("/unconfirmed")
def unconfirmed():
    if current_user.confirmed:
        return redirect(url_for("main.index"))
    return render_template("auth/unconfirmed.html")


@bp.route("/confirm")
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(to=current_user.email,
               subject="Confirmation de votre adresse mail",
               template="email/confirm",
               user=current_user,
               token=token)
    flash("Un email de confirmation a été envoyé", "info")
    return redirect(url_for("auth.unconfirmed"))


@bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    title = "Connexion"

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
            return render_template("auth/login.html",
                                   form=form,
                                   title=title)

        is_password_correct = user.verify_password(form.password.data)
        if not is_password_correct:
            form.username.errors.append("Identifiants incorrects")
            form.password.errors.append("")
            return render_template("auth/login.html",
                                   form=form,
                                   title=title)

        # Otherwise log the user in
        login_user(user, remember=form.remember_me.data)
        session["signed"] = True
        session["username"] = user.username
        flash("Tu es à présent connecté", "success")

        # Redirect the user to the page he initially wanted to access
        if session.get("next"):
            next_page = session.get("next")
            session.pop("next")
            return redirect(next_page)
        else:
            return redirect(url_for("main.index"))

    session["next"] = request.args.get("next")
    return render_template("auth/login.html",
                           form=form,
                           title=title)


@bp.route("/logout")
def logout():
    session.pop("signed", None)
    session.pop("username", None)
    logout_user()
    return redirect(url_for("main.index"))


@bp.route("/confirm/<token>")
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for("main.index"))
    if current_user.confirm(token):
        flash("Ton compte est à présent validé", "success")
    else:
        flash("Ce lien de confirmation est invalide", "error")
    return redirect(url_for("main.index"))
