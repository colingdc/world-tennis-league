from flask import render_template

from .. import bp
from ..lib import fetch_all_tournaments
from ...decorators import login_required


@bp.route("/view")
@login_required
def view_tournaments():
    tournaments = fetch_all_tournaments()

    return render_template(
        "tournament/view_tournaments.html",
        title="Tournois",
        tournaments=tournaments
    )
