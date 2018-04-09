from .base import * # noqua


DEBUG = env.bool('DJANGO_DEBUG', default=True)
CORS_ORIGIN_WHITELIST = (
    'localhost:3000',
)