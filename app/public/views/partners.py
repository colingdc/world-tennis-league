from flask import render_template

from .. import bp


@bp.route("/partners")
def partners():
    return render_template("public/partners.html")
