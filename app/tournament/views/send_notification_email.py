from datetime import datetime

from flask import redirect, url_for

from .. import bp
from ... import db
from ...decorators import manager_required
from ...email import send_email
from ...models import Tournament, User
from ...notifications import display_info_message
from ...wordings import wordings


@bp.route("/<tournament_id>/send_notification_email")
@manager_required
def send_notification_email(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)

    if all(t.notification_sent_at is not None for t in tournament.week.tournaments):
        display_info_message(wordings["participants_already_notified"])
        return redirect(url_for(".view_tournament", tournament_id=tournament.id))

    for t in tournament.week.tournaments:
        t.notification_sent_at = datetime.now()
        db.session.add(t)
    db.session.commit()

    users_to_notify = User.query.filter(User.notifications_activated).filter(User.confirmed)

    for user in users_to_notify:
        send_email(
            user.email,
            wordings["registrations_opened_this_week"],
            "email/registrations_open",
            user=user,
            tournaments=tournament.week.tournaments
        )

    display_info_message(wordings["participants_notified"])
    return redirect(url_for(".view_tournament", tournament_id=tournament.id))
