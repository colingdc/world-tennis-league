from flask import redirect, url_for
from flask_login import current_user

from .. import bp
from ... import db
from ...decorators import login_required
from ...models import Tournament, Participation
from ...notifications import display_warning_message, display_success_message
from ...wordings import wordings


@bp.route("/<tournament_id>/register")
@login_required
def register(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)

    if not current_user.can_register_to_tournament(tournament):
        display_warning_message(wordings["not_allowed_to_register"])
        return redirect(url_for(".view_tournament", tournament_id=tournament_id))

    participant = Participation(
        tournament_id=tournament_id,
        user_id=current_user.id
    )

    db.session.add(participant)
    db.session.commit()

    display_success_message(wordings["registration_confirmed"].format(tournament.name))
    return redirect(url_for(".view_tournament", tournament_id=tournament_id))
