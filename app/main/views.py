from flask import redirect, render_template, url_for
from flask_login import current_user

from . import bp
from ..decorators import manager_required, login_required
from ..models import Ranking, Tournament, User


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


@bp.route("/rules")
def rules():
    title = "FAQ"
    return render_template("main/rules.html",
                           title=title)
