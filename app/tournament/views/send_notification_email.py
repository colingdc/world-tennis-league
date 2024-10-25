from datetime import datetime

from .. import bp
from ..lib import fetch_tournament
from ... import db
from ...decorators import manager_required
from ...email import send_email
from ...navigation import go_to_tournament_page
from ...notifications import display_info_message
from ...user.lib import fetch_users_that_can_receive_notifications
from ...wordings import wordings


@bp.route("/<tournament_id>/send_notification_email")
@manager_required
def send_notification_email(tournament_id):
    tournament = fetch_tournament(tournament_id)

    if all(t.notification_sent_at is not None for t in tournament.week.tournaments):
        display_info_message(wordings["participants_already_notified"])
        return go_to_tournament_page(tournament.id)

    for t in tournament.week.tournaments:
        t.notification_sent_at = datetime.now()
        db.session.add(t)
    db.session.commit()

    users_to_notify = fetch_users_that_can_receive_notifications()

    for user in users_to_notify:
        send_email(
            user.email,
            wordings["registrations_opened_this_week"],
            "email/registrations_open",
            user=user,
            tournaments=tournament.week.tournaments
        )

    display_info_message(wordings["participants_notified"])
    return go_to_tournament_page(tournament.id)
