from .. import db
from ..models import TournamentWeek


def insert_tournament_week(start_date):
    tournament_week = TournamentWeek(start_date=start_date)
    db.session.add(tournament_week)
    db.session.commit()


def fetch_tournament_week_by_start_date(start_date):
    return TournamentWeek.query.filter_by(start_date=start_date).first()
