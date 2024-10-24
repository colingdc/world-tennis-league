from flask import render_template

from .. import bp
from ...decorators import login_required
from ...models import Tournament


@bp.route("/<tournament_id>/stats")
@login_required
def stats(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)

    return render_template(
        "tournament/stats.html",
        tournament=tournament
    )
