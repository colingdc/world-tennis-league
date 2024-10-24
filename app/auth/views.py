from flask import current_app, redirect, render_template, request, session, url_for
from flask_login import current_user, login_user, logout_user

from . import bp
from .forms import ChangePasswordForm, LoginForm, PasswordResetForm, PasswordResetRequestForm, SignupForm
from .. import db
from ..decorators import login_required, auth_required
from ..email import send_email
from ..models import Role, User
from ..notifications import display_success_message, display_info_message, display_danger_message, display_error_message


@bp.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm(request.form)

    if form.validate_on_submit():
        user_exists = User.query.filter_by(username=form.username.data).first()
        email_exists = User.query.filter_by(email=form.email.data).first()
        if user_exists:
            form.username.errors.append("Ce nom d'utilisateur est déjà pris")
        if email_exists:
            form.email.errors.append("Cet email existe déjà")
        if user_exists or email_exists:
            return render_template(
                "auth/signup.html",
                title="Inscription",
                form=form
            )
        else:
            role = Role.query.filter(Role.name == "User").first()
            user = User(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data,
                role=role
            )
            db.session.add(user)
            db.session.commit()
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
        return render_template(
            "auth/signup.html",
            title="Inscription",
            form=form
        )


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
    send_email(
        to=current_user.email,
        subject="Confirmation de ton adresse mail",
        template="email/confirm",
        user=current_user,
        token=token
    )
    display_info_message("Un email de confirmation t'a été envoyé.")
    return redirect(url_for("auth.unconfirmed"))


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

        print(session)
        return redirect(url_for("auth.unconfirmed"))

    return render_template(
        "auth/login.html",
        title="Connexion",
        form=form
    )


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
        display_success_message("Ton compte est à présent validé.")
        return redirect(url_for("main.index"))
    else:
        display_danger_message("Ce lien de confirmation est invalide ou a expiré.")
        return redirect(url_for("auth.unconfirmed"))


@bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            display_success_message("Ton mot de passe a été mis à jour.")
            return redirect(url_for("main.index"))
        else:
            form.old_password.errors.append("Mot de passe incorrect")
    return render_template(
        "auth/change_password.html",
        title="Changement de mot de passe",
        form=form,
        user=current_user
    )


@bp.route("/reset", methods=["GET", "POST"])
def reset_password_request():
    if not current_user.is_anonymous():
        return redirect(url_for("main.index"))
    form = PasswordResetRequestForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
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


@bp.route("/reset/<token>", methods=["GET", "POST"])
def reset_password(token):
    if not current_user.is_anonymous():
        return redirect(url_for("main.index"))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            display_error_message("L'adresse email entrée ne correspond pas au lien de "
                                  "réinitialisation envoyé.")
            return render_template(
                "auth/reset_password.html",
                title="Réinitialisation du mot de passe",
                form=form,
                token=token
            )
        if user.reset_password(token, form.password.data):
            display_success_message("Ton mot de passe a été mis à jour.")
            login_user(user)
            return redirect(url_for("main.index"))
        else:
            display_error_message("L'adresse email entrée ne correspond pas au lien de "
                                  "réinitialisation envoyé.")
            return render_template(
                "auth/reset_password.html",
                title="Réinitialisation du mot de passe",
                form=form,
                token=token
            )
    return render_template(
        "auth/reset_password.html",
        title="Réinitialisation du mot de passe",
        form=form,
        token=token
    )
