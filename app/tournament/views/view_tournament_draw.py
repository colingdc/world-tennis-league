from flask import abort, render_template

from .. import bp
from ...decorators import login_required
from ...models import Tournament


@bp.route("/<tournament_id>/draw")
@login_required
def view_tournament_draw(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)

    if tournament.deleted_at:
        abort(404)

    return render_template(
        "tournament/view_tournament_draw.html",
        title=f"{tournament.name} – Tableau",
        tournament=tournament
    )
