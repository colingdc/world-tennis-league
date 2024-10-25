from flask import redirect, url_for

from .. import bp
from ...decorators import manager_required
from ...models import Player
from ...notifications import display_info_message, display_danger_message


@bp.route("/<player_id>/delete")
@manager_required
def delete_player(player_id):
    player = Player.query.get_or_404(player_id)

    if player.tournament_players.count() > 0:
        tournament = player.tournament_players.first().tournament

        display_danger_message("Ce joueur ne peut pas être supprimé car il apparait dans le "
                               f"tableau d'au moins un tournoi ({tournament.name})")

        return redirect(url_for(".view_players"))

    player.delete()

    display_info_message(f"Le joueur {player.get_name()} a été supprimé")

    return redirect(url_for(".view_players"))
