from flask_babel import _
from flask_login import current_user

from .. import bp
from ..lib import fetch_tournament
from ...decorators import login_required
from ...navigation import go_to_tournament_page
from ...notifications import display_warning_message, display_success_message


@bp.route("/<tournament_id>/withdraw")
@login_required
def withdraw(tournament_id):
    tournament = fetch_tournament(tournament_id)

    if not current_user.get_participation(tournament):
        display_warning_message(_("not_registered_yet"))
        return go_to_tournament_page(tournament_id)

    participation = current_user.get_participation(tournament)

    if not tournament.is_open_to_registration():
        display_warning_message(_("not_allowed_to_withdraw"))
    else:
        participation.delete()
        display_success_message(_("withdrawal_confirmed", tournament_name=tournament.name))

    return go_to_tournament_page(tournament_id)
