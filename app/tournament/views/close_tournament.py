from flask_babel import _

from .. import bp
from ..lib import is_tournament_finished, finish_tournament, fetch_tournament
from ...decorators import manager_required
from ...navigation import go_to_tournament_page
from ...notifications import display_info_message


@bp.route("/<tournament_id>/close_tournament")
@manager_required
def close_tournament(tournament_id):
    tournament = fetch_tournament(tournament_id)

    if not is_tournament_finished(tournament):
        finish_tournament(tournament)
        display_info_message(_("tournament_closed"))

    return go_to_tournament_page(tournament_id)
