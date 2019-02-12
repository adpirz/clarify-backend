from .base import * # noqa


CORS_ORIGIN_WHITELIST = (
    'app.clarify.school',
    'demo.clarify.school',
    'alpha.clarify.school'
)



CORS_ALLOW_CREDENTIALS = True

ALLOWED_HOSTS = [
    'app.api.clarify.school',
    'demo.api.clarify.school',
    'alpha.api.clarify.school'
]

SESSION_COOKIE_DOMAIN = '.clarify.school'
CSRF_COOKIE_DOMAIN = '.clarify.school'
CSRF_TRUSTED_ORIGINS = ['.clarify.school']

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

if DEBUG:
    LOGGING = {
        'version': 1,
        'filters': {
            'require_debug_true': {
                '()': 'django.utils.log.RequireDebugTrue',
            }
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'filters': ['require_debug_true'],
                'class': 'logging.StreamHandler',
            }
        },
        'loggers': {
            'django.db.backends': {
                'level': 'DEBUG',
                'handlers': [],
            }
        }
    }