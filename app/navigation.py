from flask import redirect, url_for


def go_to_homepage():
    return redirect(url_for("main.index"))

