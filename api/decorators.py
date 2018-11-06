from functools import wraps

from django.http import JsonResponse

from sis_pull.models import Staff


def require_methods(*method_list):
    # JsonResponse version of
    # https://docs.djangoproject.com/en/1.11/_modules
    # /django/views/decorators/http/#require_http_methods

    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            if request.method not in method_list:
                return JsonResponse({
                    "error": f"Method '{request.method}' not allowed."
                }, status=405)
            return func(request, *args, **kwargs)
        return inner
    return decorator


def requires_staff(func):
    """Passes requires_staff as second argument or sends error"""

    @wraps(func)
    def inner(request, *args, **kwargs):
        try:
            requesting_staff = request.user.staff
        except Staff.DoesNotExist:
            return JsonResponse({
                "error": "No staff exists for this user"
            }, status=401)
        return func(request, requesting_staff, *args, **kwargs)
    return inner
