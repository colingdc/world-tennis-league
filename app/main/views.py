from flask import redirect, render_template, url_for, request, flash
from flask_login import current_user

from . import bp
from .forms import SettingsForm
from .lib import generate_chart
from .. import db
from ..decorators import manager_required, login_required
from ..models import Tournament, User


@bp.route("/")
def index():
    if current_user.is_authenticated:
        ongoing_tournaments = Tournament.get_ongoing_tournaments()
        open_tournaments = Tournament.get_open_tournaments()
        return render_template("main/dashboard.html",
                               ongoing_tournaments=ongoing_tournaments,
                               open_tournaments=open_tournaments,
                               user=current_user)
    return redirect(url_for("auth.login"))


@bp.route("/user/<user_id>")
@login_required
def view_user(user_id):
    user = User.query.get_or_404(user_id)
    title = f"Profil de {user.username}"

    rankings = generate_chart(user)

    series = [{"name": "Classement",
               "data": [{"x": int(t.started_at.strftime("%s")) * 1000,
                         "y": t.year_to_date_ranking or "null",
                         "tournament_name": t.name}
                        for t in rankings]}]

    return render_template("main/view_user.html",
                           title=title,
                           series=series,
                           user=user)


@bp.route("/user/settings", methods=["GET", "POST"])
@login_required
def settings():
    title = "Paramètres"
    form = SettingsForm(request.form)

    if request.method == "GET":
        form.notifications_activated.data = current_user.notifications_activated
    if form.validate_on_submit():
        current_user.notifications_activated = form.notifications_activated.data
        db.session.add(current_user)
        db.session.commit()
        flash(f"Tes préférences de notifications ont été mises à jour", "info")
    return render_template("main/settings.html",
                           title=title,
                           form=form,
                           user=current_user
                           )


@bp.route("/user/view")
@manager_required
def view_users():
    title = "Utilisateurs"
    users = User.query.order_by(User.username)
    return render_template("main/view_users.html",
                           title=title,
                           users=users)


@bp.route("/user/raw")
@manager_required
def view_users_raw():
    title = "Utilisateurs"
    users = User.query.order_by(User.username)
    users = [user for user in users if not user.email.startswith("TEMPORARY")]
    return render_template("main/view_users_raw.html",
                           title=title,
                           users=users)


@bp.route("/rules")
def rules():
    title = "FAQ"
    return render_template("main/rules.html",
                           title=title)
