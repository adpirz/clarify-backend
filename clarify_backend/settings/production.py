from .base import * # noqa

CORS_ORIGIN_WHITELIST = (
    'app.clarify.school',
)

CORS_ALLOW_CREDENTIALS = True

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', default='api.clarify.school')