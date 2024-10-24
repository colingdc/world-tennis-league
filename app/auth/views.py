from flask import current_app, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_user, logout_user

from . import bp
from .. import db
from ..decorators import login_required, auth_required
from ..email import send_email
from ..models import Role, User
from .forms import ChangePasswordForm, LoginForm, PasswordResetForm, PasswordResetRequestForm, SignupForm


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
            role = Role.query.filter(Role.name == "User").first()
            user = User(username=form.username.data,
                        email=form.email.data,
                        password=form.password.data,
                        role=role)
            db.session.add(user)
            db.session.commit()
            token = user.generate_confirmation_token()
            send_email(to=user.email,
                       subject="Confirmation de ton adresse mail",
                       template="email/confirm",
                       user=user,
                       token=token)

            send_email(to=current_app.config.get("ADMIN_WTL"),
                       subject="Nouvel inscrit",
                       template="email/new_user",
                       user=user)

            flash("Un email de confirmation t'a été envoyé.", "info")
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
    if session.get("next"):
        next_page = session.get("next")
        session.pop("next")
        return redirect(next_page)
    return render_template("auth/unconfirmed.html")


@bp.route("/confirm")
@auth_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(to=current_user.email,
               subject="Confirmation de ton adresse mail",
               template="email/confirm",
               user=current_user,
               token=token)
    flash("Un email de confirmation t'a été envoyé.", "info")
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
        flash("Tu es à présent connecté.", "success")

        print(session)
        return redirect(url_for("auth.unconfirmed"))

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
@auth_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for("main.index"))
    if current_user.confirm(token):
        flash("Ton compte est à présent validé.", "success")
        return redirect(url_for("main.index"))
    else:
        flash("Ce lien de confirmation est invalide ou a expiré.", "danger")
        return redirect(url_for("auth.unconfirmed"))


@bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    title = "Changement de mot de passe"
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            flash("Ton mot de passe a été mis à jour.", "success")
            return redirect(url_for("main.index"))
        else:
            form.old_password.errors.append("Mot de passe incorrect")
    return render_template("auth/change_password.html",
                           form=form,
                           title=title,
                           user=current_user)


@bp.route("/reset", methods=["GET", "POST"])
def reset_password_request():
    if not current_user.is_anonymous():
        return redirect(url_for("main.index"))
    form = PasswordResetRequestForm()
    title = "Réinitialisation du mot de passe"
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, "Réinitialisation du mot de passe",
                       "email/reset_password",
                       user=user,
                       token=token,
                       next=request.args.get("next"))
        flash("Un email contenant des instructions pour réinitialiser "
              "ton mot de passe t'a été envoyé. Si tu n'as pas reçu d'email, "
              "vérifie dans ton dossier de spams et assure toi d'avoir rentré "
              "la bonne adresse mail.",
              "info")
        return redirect(url_for("auth.login"))
    return render_template("auth/reset_password_request.html",
                           form=form,
                           title=title)


@bp.route("/reset/<token>", methods=["GET", "POST"])
def reset_password(token):
    if not current_user.is_anonymous():
        return redirect(url_for("main.index"))
    form = PasswordResetForm()
    title = "Réinitialisation du mot de passe"
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash("L'adresse email entrée ne correspond pas au lien de "
                  "réinitialisation envoyé.", "error")
            return render_template("auth/reset_password.html",
                                   form=form,
                                   token=token,
                                   title=title)
        if user.reset_password(token, form.password.data):
            flash("Ton mot de passe a été mis à jour.", "success")
            login_user(user)
            return redirect(url_for("main.index"))
        else:
            flash("L'adresse email entrée ne correspond pas au lien de "
                  "réinitialisation envoyé.", "error")
            return render_template("auth/reset_password.html",
                                   form=form,
                                   token=token,
                                   title=title)
    return render_template("auth/reset_password.html",
                           form=form,
                           token=token,
                           title=title)
