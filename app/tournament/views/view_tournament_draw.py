from flask import abort, render_template

from .. import bp
from ...decorators import login_required
from ...models import Tournament
from ...wordings import wordings


@bp.route("/<tournament_id>/draw")
@login_required
def view_tournament_draw(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)

    if tournament.deleted_at:
        abort(404)

    return render_template(
        "tournament/view_tournament_draw.html",
        title=wordings["tournament_draw"].format(tournament.name),
        tournament=tournament
    )
