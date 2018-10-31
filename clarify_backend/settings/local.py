from .base import * # noqua


DEBUG = env.bool('DJANGO_DEBUG', default=True)
DISABLE_LOGGING = env.bool('DISABLE_LOGGING', default=False)
CORS_ORIGIN_WHITELIST = (
    'localhost:3000',
)

ALLOWED_HOSTS = ['*']

CORS_ALLOW_CREDENTIALS = True

# django-debug-toolbar
# ------------------------------------------------------------------------------

MIDDLEWARE_CLASSES += ['debug_toolbar.middleware.DebugToolbarMiddleware', ]
INSTALLED_APPS += ['debug_toolbar', 'experiment.apps.ExperimentConfig']

INTERNAL_IPS = ['127.0.0.1', '10.0.2.2', ]

DEBUG_TOOLBAR_CONFIG = {
    'DISABLE_PANELS': [
        'debug_toolbar.panels.redirects.RedirectsPanel',
    ],
}

SHELL_PLUS_PRE_IMPORTS = [
    ('pprint', 'pprint'),
    ('experiment.management.commands._experiment', '*'),
    ('deltas.tasks', '*')
]

if DEBUG and not DISABLE_LOGGING:
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
                'handlers': ['console'],
            }
        }
    }
