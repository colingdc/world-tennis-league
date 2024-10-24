from flask import redirect, url_for

from .. import bp
from ..lib import is_tournament_finished, finish_tournament
from ...decorators import manager_required
from ...models import Tournament
from ...notifications import display_info_message
from ...wordings import wordings


@bp.route("/<tournament_id>/close_tournament")
@manager_required
def close_tournament(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)

    if not is_tournament_finished(tournament):
        finish_tournament(tournament)
        display_info_message(wordings["tournament_closed"])

    return redirect(url_for(".view_tournament", tournament_id=tournament.id))
