from flask import render_template

from .. import bp
from ..lib import fetch_tournament
from ...decorators import login_required


@bp.route("/<tournament_id>/stats")
@login_required
def stats(tournament_id):
    tournament = fetch_tournament(tournament_id)

    return render_template(
        "tournament/stats.html",
        tournament=tournament
    )
