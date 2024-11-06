from flask import render_template

from .. import bp
from ..lib import fetch_player_by_id
from ...decorators import manager_required


@bp.route("/<player_id>")
@manager_required
def view_player(player_id):
    player = fetch_player_by_id(player_id)

    return render_template(
        "player/view_player.html",
        title=player.get_standard_name(),
        player=player
    )
