from math import floor, log

from .. import db
from ..constants import tournament_categories
from ..models import Tournament, TournamentStatus, TournamentWeek, Ranking, Match


def fetch_tournament(tournament_id):
    return Tournament.query.get_or_404(tournament_id)


def insert_tournament_week(start_date):
    tournament_week = TournamentWeek(start_date=start_date)
    db.session.add(tournament_week)
    db.session.commit()


def fetch_tournament_week_by_start_date(start_date):
    return TournamentWeek.query.filter_by(start_date=start_date).first()


def insert_tournament(name, start_date, week_id, category_name):
    category = tournament_categories.get(category_name)
    number_rounds = category["number_rounds"]

    tournament = Tournament(
        name=name,
        started_at=start_date,
        week_id=week_id,
        number_rounds=number_rounds,
        category=category_name,
    )

    db.session.add(tournament)
    db.session.commit()

    for i in range(1, 2 ** number_rounds):
        match = Match(
            position=i,
            tournament_id=tournament.id,
            round=floor(log(i) / log(2)) + 1
        )
        db.session.add(match)
    db.session.commit()


def open_tournament_registrations(tournament):
    tournament.status = TournamentStatus.REGISTRATION_OPEN

    db.session.add(tournament)
    db.session.commit()


def close_tournament_registrations(tournament):
    tournament.status = TournamentStatus.ONGOING

    db.session.add(tournament)
    db.session.commit()

    for participant in tournament.participations:
        if not participant.has_made_forecast():
            db.session.delete(participant)
    db.session.commit()


def finish_tournament(tournament):
    tournament.status = TournamentStatus.FINISHED

    db.session.add(tournament)
    db.session.commit()

    tournament.compute_scores()
    Ranking.compute_rankings(tournament.week)


def is_tournament_finished(tournament):
    return tournament.status == TournamentStatus.FINISHED


def fetch_non_deleted_tournaments():
    return Tournament.query.filter(Tournament.deleted_at.is_(None))


def fetch_ongoing_tournaments():
    return (
        Tournament.query
            .order_by(Tournament.started_at.desc())
            .filter(Tournament.deleted_at.is_(None))
            .filter(Tournament.status == TournamentStatus.ONGOING)
    )


def fetch_open_tournaments():
    return (
        Tournament.query
            .order_by(Tournament.started_at.desc())
            .filter(Tournament.deleted_at.is_(None))
            .filter(Tournament.status == TournamentStatus.REGISTRATION_OPEN)
    )
