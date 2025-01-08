from flask import render_template

from .. import bp
from ...decorators import manager_required
from ...models import Player


@bp.route("/view")
@manager_required
def view_players():
    players = Player.query.order_by(Player.last_name, Player.first_name)

    return render_template(
        "player/view_players.html",
        title="Joueurs",
        players=players
    )
