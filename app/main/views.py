from flask import render_template, redirect, url_for, flash, current_app
from flask_login import current_user, login_required

from . import bp
from ..decorators import manager_required
from .forms import ContactForm
from ..email import send_email
from ..models import User, Ranking


@bp.route("/")
def index():
    if current_user.is_authenticated:
        return render_template("main/dashboard.html",
                               user=current_user)
    return render_template("main/index.html")


@bp.route("/contact", methods=['GET', 'POST'])
def contact():
    title = "Contact"
    form = ContactForm()
    if form.validate_on_submit():
        message = form.message.data
        if current_user:
            sender = current_user.username
        else:
            sender = "un utilisateur non connecté"
        send_email(to=current_app.config["ADMIN_WTL"],
                   subject="Nouveau message de la part de {}".format(sender),
                   template="email/contact",
                   message=message,
                   email=form.email.data,
                   user=current_user)
        flash(u"Ton message a bien été envoyé.", "success")
        return redirect(url_for(".contact"))

    return render_template("main/contact.html",
                           form=form,
                           title=title)


@bp.route("/user/<user_id>")
@login_required
def view_user(user_id):
    user = User.query.get_or_404(user_id)
    title = f"Profil de {user.username}"

    rankings = Ranking.generate_chart(user)

    series = [{"name": "Classement",
               "data": [{"x": int(t.started_at.strftime("%s")) * 1000,
                         "y": t.year_to_date_ranking or "null",
                         "tournament_name": t.name}
                        for t in rankings]}]

    return render_template("main/view_user.html",
                           title=title,
                           series=series,
                           user=user)


@bp.route("/user/view")
@manager_required
def view_users():
    title = "Utilisateurs"
    users = User.query.order_by(User.username)
    return render_template("main/view_users.html",
                           title=title,
                           users=users)
