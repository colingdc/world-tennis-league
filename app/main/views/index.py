from flask import redirect, render_template, url_for
from flask_login import current_user

from .. import bp
from ...models import Tournament


@bp.route("/")
def index():
    if current_user.is_authenticated:
        ongoing_tournaments = Tournament.get_ongoing_tournaments()
        open_tournaments = Tournament.get_open_tournaments()

        return render_template(
            "main/dashboard.html",
            ongoing_tournaments=ongoing_tournaments,
            open_tournaments=open_tournaments,
            user=current_user
        )

    return redirect(url_for("auth.login"))
