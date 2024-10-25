from .. import bp
from ..lib import close_tournament_registrations, fetch_tournament
from ...decorators import manager_required
from ...navigation import go_to_tournament_page
from ...notifications import display_info_message
from ...wordings import wordings


@bp.route("/<tournament_id>/close_registrations")
@manager_required
def close_registrations(tournament_id):
    tournament = fetch_tournament(tournament_id)

    close_tournament_registrations(tournament)

    display_info_message(wordings["registrations_closed"])
    return go_to_tournament_page(tournament_id)
