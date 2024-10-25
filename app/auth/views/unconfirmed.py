from flask import redirect, render_template, session, url_for
from flask_login import current_user

from .. import bp


@bp.route("/unconfirmed")
def unconfirmed():
    if current_user.confirmed:
        return redirect(url_for("main.index"))

    if session.get("next"):
        next_page = session.get("next")
        session.pop("next")
        return redirect(next_page)

    return render_template("auth/unconfirmed.html")
