from flask import render_template

from .. import bp
from ...wordings import wordings


@bp.route("/rules")
def rules():
    return render_template(
        "main/rules.html",
        title=wordings["faq"]
    )
