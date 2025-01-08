from flask import render_template

from .. import bp


@bp.route("/networks")
def networks():
    return render_template("public/networks.html")
