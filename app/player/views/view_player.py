from flask import render_template

from .. import bp
from ...decorators import manager_required
from ...models import Player


@bp.route("/<player_id>")
@manager_required
def view_player(player_id):
    player = Player.query.get_or_404(player_id)

    return render_template(
        "player/view_player.html",
        title=player.get_name(),
        player=player
    )
