from flask import abort, render_template

from .. import bp
from ..lib import fetch_tournament
from ...decorators import login_required


@bp.route("/<tournament_id>/draw")
@login_required
def view_tournament_draw(tournament_id):
    tournament = fetch_tournament(tournament_id)

    if tournament.deleted_at:
        abort(404)

    return render_template(
        "tournament/view_tournament_draw.html",
        title=f"{tournament.name} – Tableau",
        tournament=tournament
    )
