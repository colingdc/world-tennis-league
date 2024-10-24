from ..models import Tournament, TournamentWeek, Ranking


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
