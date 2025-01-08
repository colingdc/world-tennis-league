from flask import render_template
from flask_babel import _

from .. import bp
from ..lib import get_weekly_ranking
from ...decorators import login_required
from ...models import TournamentWeek


@bp.route("/<tournament_week_id>")
@login_required
def weekly_ranking(tournament_week_id):
    week = TournamentWeek.query.get_or_404(tournament_week_id)

    ranking = get_weekly_ranking(week)

    return render_template(
        "ranking/ranking.html",
        title=_("ranking"),
        ranking=ranking,
        week=week
    )
