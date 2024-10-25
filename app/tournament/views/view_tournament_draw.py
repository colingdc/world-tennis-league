from flask import abort, render_template

from .. import bp
from ..lib import fetch_tournament
from ...decorators import login_required
from ...wordings import wordings


@bp.route("/<tournament_id>/draw")
@login_required
def view_tournament_draw(tournament_id):
    tournament = fetch_tournament(tournament_id)

    return render_template(
        "tournament/view_tournament_draw.html",
        title=wordings["tournament_draw"].format(tournament.name),
        tournament=tournament
    )
