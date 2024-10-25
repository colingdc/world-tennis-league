from functools import wraps

from flask import abort, request, session
from flask_login import current_user

from .models import Permission
from .navigation import go_to_account_unconfirmed_page, go_to_login_page


def permission_required(permission=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if permission is not None and not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    return permission_required(Permission.ADMINISTER)(f)


def manager_required(f):
    return permission_required(Permission.MANAGE_TOURNAMENT)(f)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return go_to_login_page()
        if not current_user.confirmed:
            return go_to_account_unconfirmed_page()
        return f(*args, **kwargs)
    return decorated_function


def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            session["next"] = request.url
            return go_to_login_page()
        return f(*args, **kwargs)
    return decorated_function
