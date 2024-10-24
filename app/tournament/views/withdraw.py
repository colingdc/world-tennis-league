from flask import redirect, url_for
from flask_login import current_user

from .. import bp
from ...decorators import login_required
from ...models import Tournament
from ...notifications import display_warning_message, display_success_message


@bp.route("/<tournament_id>/withdraw")
@login_required
def withdraw(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)

    if not current_user.participation(tournament):
        display_warning_message("Tu n'es pas inscrit à ce tournoi")
        return redirect(url_for(".view_tournament", tournament_id=tournament_id))

    participation = current_user.participation(tournament)

    if not tournament.is_open_to_registration():
        display_warning_message("Tu ne peux plus te retirer de ce tournoi")
    else:
        participation.delete()
        display_success_message(f"Tu es bien désinscrit du tournoi {tournament.name}")

    return redirect(url_for(".view_tournament", tournament_id=tournament_id))
