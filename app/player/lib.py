from .. import db
from ..models import Player


def fetch_player_by_id(player_id):
    return Player.query.get_or_404(player_id)


def fetch_sorted_players():
    return Player.query.order_by(Player.last_name, Player.first_name)


def insert_player(first_name, last_name):
    player = Player(
        first_name=first_name,
        last_name=last_name
    )

    db.session.add(player)
    db.session.commit()


def update_player(player, first_name, last_name):
    player.first_name = first_name
    player.last_name = last_name

    db.session.add(player)
    db.session.commit()
