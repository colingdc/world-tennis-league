from flask import abort, redirect, render_template, url_for

from datetime import date
from flask_babel import format_datetime
from . import bp
from ..decorators import login_required
from ..models import Ranking, Tournament, TournamentWeek, TournamentStatus
from .forms import RankingForm, MonthlyRankingForm


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


@bp.route("/monthly/", methods=["GET", "POST"])
@bp.route("/monthly/<year>/<month>", methods=["GET", "POST"])
@login_required
def monthly_ranking(year=None, month=None):
    title = "Classements par mois"

    form = MonthlyRankingForm()

    months = list(reversed(sorted(set((t.started_at.year, t.started_at.month) for t in Tournament.query))))

    def format_date(year, month):
        return format_datetime(date(int(year), int(month), 1), "MMMM yyyy").capitalize()

    form.month_name.choices = [("", "Choisir un mois")] + [
        (f"{year}-{month}", format_date(year, month)) for year, month in months]

    if form.validate_on_submit() and form.month_name.data != "":
        year, month = form.month_name.data.split("-")
        return redirect(url_for(".monthly_ranking", year=int(year), month=int(month)))

    ranking = Ranking.get_monthly_ranking(year, month) if year and month else None
    month_name = format_date(year, month) if year and month else None

    return render_template("ranking/monthly.html",
                           month_name=month_name,
                           title=title,
                           form=form,
                           ranking=ranking)


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

    if form.validate_on_submit() and form.week_name.data != -1:
        return redirect(url_for(".ranking",
                                tournament_week_id=form.week_name.data))

    return render_template("ranking/index.html",
                           title=title,
                           form=form)
