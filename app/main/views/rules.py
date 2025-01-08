from flask import render_template
from flask_babel import _

from .. import bp


@bp.route("/rules")
def rules():
    return render_template(
        "main/rules.html",
        title=_("faq")
    )
