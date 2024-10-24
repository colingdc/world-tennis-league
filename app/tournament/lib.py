from .. import db
from ..models import Tournament, TournamentStatus, TournamentWeek, Ranking


def insert_tournament_week(start_date):
    tournament_week = TournamentWeek(start_date=start_date)
    db.session.add(tournament_week)
    db.session.commit()


def fetch_tournament_week_by_start_date(start_date):
    return TournamentWeek.query.filter_by(start_date=start_date).first()


def insert_tournament(name, start_date, week_id, number_rounds, category):
    tournament = Tournament(
        name=name,
        started_at=start_date,
        week_id=week_id,
        number_rounds=number_rounds,
        category=category,
    )

    db.session.add(tournament)
    db.session.commit()

    return tournament


def open_tournament_registrations(tournament):
    tournament.status = TournamentStatus.REGISTRATION_OPEN

    db.session.add(tournament)
    db.session.commit()


def close_tournament_registrations(tournament):
    tournament.status = TournamentStatus.ONGOING

    db.session.add(tournament)
    db.session.commit()


def finish_tournament(tournament):
    tournament.status = TournamentStatus.FINISHED

    db.session.add(tournament)
    db.session.commit()

    tournament.compute_scores()
    Ranking.compute_rankings(tournament.week)


def is_tournament_finished(tournament):
    return tournament.status == TournamentStatus.FINISHED
