from .base import * # noqa


DEBUG=False

CORS_ORIGIN_WHITELIST = (
    'app.clarify.school',
    'demo.clarify.school',
)


CORS_ALLOW_CREDENTIALS = True

ALLOWED_HOSTS = ['api.clarify.school', 'demo.api.clarify.school']

SESSION_COOKIE_DOMAIN = '.clarify.school'
CSRF_COOKIE_DOMAIN = '.clarify.school'
