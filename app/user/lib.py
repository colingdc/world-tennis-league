from .. import db
from ..models import Tournament, TournamentWeek, Ranking, User, TournamentStatus


def fetch_users_that_can_receive_notifications():
    return User.query.filter(User.notifications_activated).filter(User.confirmed)


def update_notification_preferences(user, notifications_activated):
    user.notifications_activated = notifications_activated

    db.session.add(user)
    db.session.commit()


def get_participations_in_started_tournaments(user):
    return (
        user.participations
            .join(Tournament)
            .filter(Tournament.status != TournamentStatus.REGISTRATION_OPEN)
            .order_by(Tournament.started_at.desc())
            .all()
    )


def generate_chart(user):
    return (Tournament.query
            .join(TournamentWeek)
            .outerjoin(Ranking, Ranking.tournament_week_id == TournamentWeek.id)
            .filter(Ranking.user_id == user.id)
            .order_by(Tournament.started_at)
            .with_entities(Tournament.id,
                           Tournament.name,
                           Tournament.started_at,
                           Ranking.year_to_date_ranking)
            )
