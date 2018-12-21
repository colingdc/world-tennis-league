from flask import abort, flash, redirect, render_template, url_for
from flask_login import login_required

from . import bp
from .forms import RankingForm
from ..models import Ranking, Tournament


@bp.route("/<tournament_id>")
@login_required
def ranking(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    if tournament.deleted_at:
        abort(404)

    if not tournament.is_finished():
        flash("Ce tournoi n'est pas terminé", "info")
        redirect(url_for("tournament.view_tournament",
                         tournament_id=tournament_id))

    title = "Classement"
    ranking = Ranking.get_ranking(tournament)
    return render_template("ranking/ranking.html",
                           title=title,
                           ranking=ranking,
                           tournament=tournament)


@bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    title = "Classements"

    form = RankingForm()
    tournaments = Tournament.get_finished_tournaments()
    form.tournament_name.choices = [
        (-1, "Choisir un tournoi")] + [(t.id, t.name) for t in tournaments]

    if form.validate_on_submit():
        tournament = Tournament.query.get(form.tournament_name.data)
        return redirect(url_for(".ranking",
                                tournament_id=tournament.id))

    return render_template("ranking/index.html",
                           title=title,
                           form=form)
