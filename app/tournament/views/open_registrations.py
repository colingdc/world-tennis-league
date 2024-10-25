from .. import bp
from ..lib import open_tournament_registrations, fetch_tournament
from ...decorators import manager_required
from ...navigation import go_to_tournament_page
from ...notifications import display_info_message
from ...wordings import wordings


@bp.route("/<tournament_id>/open_registrations")
@manager_required
def open_registrations(tournament_id):
    tournament = fetch_tournament(tournament_id)

    open_tournament_registrations(tournament)

    display_info_message(wordings["registrations_opened"])
    return go_to_tournament_page(tournament_id)
