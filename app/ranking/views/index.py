from flask import redirect, render_template, url_for

from .. import bp
from ..forms import RankingForm
from ...decorators import login_required
from ...models import Tournament, TournamentWeek, TournamentStatus


@bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    form = RankingForm()

    weeks = (TournamentWeek.query
             .join(Tournament)
             .filter(Tournament.status == TournamentStatus.FINISHED)
             .order_by(TournamentWeek.start_date.desc()))

    form.week_name.choices = [(-1, "Choisir une semaine")] + [(w.id, w.get_name("ranking")) for w in weeks]

    if form.validate_on_submit() and form.week_name.data != -1:
        return redirect(url_for(".weekly_ranking", tournament_week_id=form.week_name.data))

    return render_template(
        "ranking/index.html",
        title="Classements",
        form=form
    )
