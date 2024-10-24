from flask import render_template

from .. import bp
from ..lib import fetch_non_deleted_tournaments
from ...decorators import login_required
from ...wordings import wordings


@bp.route("/view")
@login_required
def view_tournaments():
    tournaments = fetch_non_deleted_tournaments()

    return render_template(
        "tournament/view_tournaments.html",
        title=wordings["tournaments"],
        tournaments=tournaments
    )
