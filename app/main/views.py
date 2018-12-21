from flask import render_template
from flask_login import current_user, login_required

from . import bp
from ..models import User, Ranking


@bp.route("/")
def index():
    if current_user.is_authenticated:
        return render_template("main/dashboard.html",
                               user=current_user)
    return render_template("main/index.html")


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
