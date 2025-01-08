from flask import render_template
from flask_babel import _

from .. import bp
from ..lib import fetch_sorted_players
from ...decorators import manager_required


@bp.route("/view")
@manager_required
def view_players():
    players = fetch_sorted_players()

    return render_template(
        "player/view_players.html",
        title=_("players"),
        players=players
    )
