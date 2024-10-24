from flask import redirect, url_for
from flask_login import current_user

from .. import bp
from ...decorators import login_required
from ...models import Tournament
from ...notifications import display_warning_message, display_success_message
from ...wordings import wordings


@bp.route("/<tournament_id>/withdraw")
@login_required
def withdraw(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)

    if not current_user.participation(tournament):
        display_warning_message(wordings["not_registered_yet"])
        return redirect(url_for(".view_tournament", tournament_id=tournament_id))

    participation = current_user.participation(tournament)

    if not tournament.is_open_to_registration():
        display_warning_message(wordings["not_allowed_to_withdraw"])
    else:
        participation.delete()
        display_success_message(wordings["withdrawal_confirmed"])

    return redirect(url_for(".view_tournament", tournament_id=tournament_id))
