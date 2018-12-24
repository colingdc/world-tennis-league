from flask import abort, flash, redirect, render_template, url_for
from flask_login import login_required

from . import bp
from .forms import RankingForm
from ..models import Ranking, Tournament, TournamentWeek


@bp.route("/<tournament_week_id>")
@login_required
def ranking(tournament_week_id):
    week = TournamentWeek.query.get_or_404(tournament_week_id)
    if week.deleted_at:
        abort(404)

    title = "Classement"
    ranking = Ranking.get_ranking(week)
    return render_template("ranking/ranking.html",
                           title=title,
                           ranking=ranking,
                           week=week)


@bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    title = "Classements"

    form = RankingForm()
    tournaments = Tournament.get_finished_tournaments()
    tournaments = tournaments.order_by(Tournament.started_at.desc())
    form.tournament_name.choices = [
        (-1, "Choisir un tournoi")] + [(t.id, t.name) for t in tournaments]

    if form.validate_on_submit():
        tournament = Tournament.query.get(form.tournament_name.data)
        return redirect(url_for(".ranking",
                                tournament_week_id=tournament.week.id))

    return render_template("ranking/index.html",
                           title=title,
                           form=form)
