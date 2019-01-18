from flask import abort, redirect, render_template, url_for

from . import bp
from ..decorators import login_required
from ..models import Ranking, Tournament, TournamentWeek, TournamentStatus
from .forms import RankingForm


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


@bp.route("/latest")
@login_required
def latest_ranking():
    week = Tournament.get_latest_finished_tournament().week
    if week.deleted_at:
        abort(404)

    return redirect(url_for(".ranking", tournament_week_id=week.id))


@bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    title = "Classements"

    form = RankingForm()
    weeks = (TournamentWeek.query
             .join(Tournament)
             .filter(Tournament.status == TournamentStatus.FINISHED)
             .order_by(TournamentWeek.start_date.desc()))

    form.week_name.choices = [
        (-1, "Choisir une semaine")] + [(w.id, w.get_name("ranking"))
                                        for w in weeks]

    if form.validate_on_submit():
        return redirect(url_for(".ranking",
                                tournament_week_id=form.week_name.data))

    return render_template("ranking/index.html",
                           title=title,
                           form=form)
