from flask import render_template

from . import bp


@bp.route("/")
def index():
    return render_template("public/index.html")


@bp.route("/partners")
def partners():
    return render_template("public/partners.html")


@bp.route("/networks")
def networks():
    return render_template("public/networks.html")
