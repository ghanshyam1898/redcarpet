from functools import wraps

from django.http import JsonResponse

from accounts.models import User


def require_roles(roles_list):
    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            user = User.get_user_by_token(request)

            if user is None or user.role not in roles_list:
                response = JsonResponse({"message": "You do not have access to this api"}, status=403)
                return response

            return func(request, *args, **kwargs)

        return inner

    return decorator
