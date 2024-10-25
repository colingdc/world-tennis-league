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

    if not current_user.participation(tournament):
        display_warning_message("Tu n'es pas inscrit à ce tournoi")
        return go_to_tournament_page(tournament_id)

    participation = current_user.participation(tournament)

    if not tournament.is_open_to_registration():
        display_warning_message("Tu ne peux plus te retirer de ce tournoi")
    else:
        participation.delete()
        display_success_message(f"Tu es bien désinscrit du tournoi {tournament.name}")

    return go_to_tournament_page(tournament_id)
