from flask import redirect, url_for


def go_to_homepage():
    return redirect(url_for("main.index"))


def go_to_account_unconfirmed_page():
    return redirect(url_for("auth.unconfirmed"))


def go_to_login_page():
    return redirect(url_for("auth.login"))
