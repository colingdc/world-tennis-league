from flask import abort, render_template

from .. import bp
from ..lib import get_weekly_ranking
from ...decorators import login_required
from ...models import TournamentWeek
from ...wordings import wordings


@bp.route("/<tournament_week_id>")
@login_required
def weekly_ranking(tournament_week_id):
    week = TournamentWeek.query.get_or_404(tournament_week_id)

    ranking = get_weekly_ranking(week)

    return render_template(
        "ranking/ranking.html",
        title=wordings["ranking"],
        ranking=ranking,
        week=week
    )
