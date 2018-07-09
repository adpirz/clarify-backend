from .base import * # noqa

CORS_ORIGIN_WHITELIST = (
    'app.clarify.school',
    'demo.clarify.school',
)


CORS_ALLOW_CREDENTIALS = True

ALLOWED_HOSTS = ['api.clarify.school']