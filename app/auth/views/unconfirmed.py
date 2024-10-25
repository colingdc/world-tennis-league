from flask import redirect, render_template, session
from flask_login import current_user

from .. import bp
from ...navigation import go_to_homepage


@bp.route("/unconfirmed")
def unconfirmed():
    if current_user.confirmed:
        return go_to_homepage()

    if session.get("next"):
        next_page = session.get("next")
        session.pop("next")
        return redirect(next_page)

    return render_template("auth/unconfirmed.html")
