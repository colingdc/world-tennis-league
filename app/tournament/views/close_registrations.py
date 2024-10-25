from flask import redirect, url_for

from .. import bp
from ..lib import close_tournament_registrations, fetch_tournament
from ...decorators import manager_required
from ...notifications import display_info_message


@bp.route("/<tournament_id>/close_registrations")
@manager_required
def close_registrations(tournament_id):
    tournament = fetch_tournament(tournament_id)

    close_tournament_registrations(tournament)

    display_info_message("Les inscriptions au tournoi sont closes")
    return redirect(url_for(".view_tournament", tournament_id=tournament.id))
