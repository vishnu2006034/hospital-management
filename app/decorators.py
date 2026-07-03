from functools import wraps
from flask import abort
from flask_login import current_user

def roles_required(*roles):
    """Decorator to restrict access to specific roles.

    If the current user is not authenticated or does not have at least one of the
    required roles, they will receive a 403 Forbidden error.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or not any(current_user.has_role(role) for role in roles):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
