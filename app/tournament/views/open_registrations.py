from flask import redirect, url_for

from .. import bp
from ..lib import open_tournament_registrations, fetch_tournament
from ...decorators import manager_required
from ...notifications import display_info_message


@bp.route("/<tournament_id>/open_registrations")
@manager_required
def open_registrations(tournament_id):
    tournament = fetch_tournament(tournament_id)

    open_tournament_registrations(tournament)

    display_info_message("Les inscriptions au tournoi sont ouvertes")
    return redirect(url_for(".view_tournament", tournament_id=tournament.id))
