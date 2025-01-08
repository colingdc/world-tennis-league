from flask import render_template
from flask_login import current_user

from .. import bp
from ...navigation import go_to_login_page
from ...tournament.lib import fetch_ongoing_tournaments, fetch_open_tournaments


@bp.route("/")
def index():
    if current_user.is_authenticated:
        ongoing_tournaments = fetch_ongoing_tournaments()
        open_tournaments = fetch_open_tournaments()

        return render_template(
            "main/dashboard.html",
            ongoing_tournaments=ongoing_tournaments,
            open_tournaments=open_tournaments,
            user=current_user
        )

    return go_to_login_page()
