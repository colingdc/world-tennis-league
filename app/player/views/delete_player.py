from flask import redirect, url_for

from .. import bp
from ..lib import fetch_player_by_id
from ...decorators import manager_required
from ...notifications import display_info_message, display_danger_message
from ...wordings import wordings


@bp.route("/<player_id>/delete")
@manager_required
def delete_player(player_id):
    player = fetch_player_by_id(player_id)

    if player.tournament_players.count() > 0:
        tournament = player.tournament_players.first().tournament

        display_danger_message(wordings["player_in_use"].format(tournament.name))

        return redirect(url_for(".view_players"))

    player.delete()

    display_info_message(wordings["player_deleted"].format(player.get_name()))

    return redirect(url_for(".view_players"))
