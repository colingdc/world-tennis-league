from datetime import datetime

from flask import redirect, url_for

from .. import bp
from ..lib import fetch_tournament
from ... import db
from ...decorators import manager_required
from ...email import send_email
from ...notifications import display_info_message
from ...user.lib import fetch_users_that_can_receive_notifications


@bp.route("/<tournament_id>/send_notification_email")
@manager_required
def send_notification_email(tournament_id):
    tournament = fetch_tournament(tournament_id)

    if all(t.notification_sent_at is not None for t in tournament.week.tournaments):
        display_info_message("La notification par mail a déjà été envoyée pour tous les tournois de la semaine")
        return redirect(url_for(".view_tournament", tournament_id=tournament.id))

    for t in tournament.week.tournaments:
        t.notification_sent_at = datetime.now()
        db.session.add(t)
    db.session.commit()

    users_to_notify = fetch_users_that_can_receive_notifications()

    for user in users_to_notify:
        send_email(
            user.email,
            "Les tournois de la semaine sont ouverts aux inscriptions !",
            "email/registrations_open",
            user=user,
            tournaments=tournament.week.tournaments
        )

    display_info_message("Les participants ont été notifiés par mail de l'ouverture des tournois de la semaine")
    return redirect(url_for(".view_tournament", tournament_id=tournament.id))
