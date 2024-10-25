from flask import render_template

from .. import bp


@bp.route("/rules")
def rules():
    return render_template(
        "main/rules.html",
        title="FAQ"
    )
