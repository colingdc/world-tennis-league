from sqlalchemy import func

from ..models import Tournament, Ranking


def get_monthly_ranking(year, month):
    tournaments = (Tournament
                   .query
                   .filter(func.year(Tournament.started_at) == year)
                   .filter(func.month(Tournament.started_at) == month))
    scores = {}

    print(tournaments.count(), "tournaments")
    for tournament in tournaments:
        for participant in tournament.participations:
            user = participant.user
            if scores.get(user) is None:
                scores[user] = {
                    "score": 0,
                    "number_of_tournaments": 0
                }
            scores[user]["number_of_tournaments"] += 1
            if participant.points is not None:
                scores[user]["score"] += participant.points
    return sorted(scores.items(), key=lambda x: -x[1]["score"])


def get_weekly_ranking(week=None):
    if week is None:
        week = Tournament.get_latest_finished_tournament().week
    ranking = (Ranking.query
               .filter(Ranking.tournament_week_id == week.id)
               .order_by(Ranking.year_to_date_ranking)
               )
    return ranking
