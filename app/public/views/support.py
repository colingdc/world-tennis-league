from flask import render_template

from .. import bp


@bp.route("/support")
def support():
    return render_template("public/support.html")
