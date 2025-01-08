from flask import render_template
from flask_babel import _

from .. import bp
from ..lib import fetch_tournament
from ...decorators import login_required


@bp.route("/<tournament_id>/draw")
@login_required
def view_tournament_draw(tournament_id):
    tournament = fetch_tournament(tournament_id)

    return render_template(
        "tournament/view_tournament_draw.html",
        title=_("tournament_draw", tournament_name=tournament.name),
        tournament=tournament
    )
