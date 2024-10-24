from flask import redirect, url_for

from .. import bp
from ..lib import close_tournament_registrations
from ...decorators import manager_required
from ...models import Tournament
from ...notifications import display_info_message


@bp.route("/<tournament_id>/close_registrations")
@manager_required
def close_registrations(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)

    close_tournament_registrations(tournament)

    display_info_message("Les inscriptions au tournoi sont closes")
    return redirect(url_for(".view_tournament", tournament_id=tournament.id))
