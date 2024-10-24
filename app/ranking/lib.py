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
            scores[user]["score"] += participant.points
            scores[user]["number_of_tournaments"] += 1
    return sorted(scores.items(), key=lambda x: -x[1]["score"])


def get_weekly_ranking(week):
    return (Ranking.query
            .filter(Ranking.tournament_week_id == week.id)
            .order_by(Ranking.year_to_date_ranking)
            )
