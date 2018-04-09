from .base import * # noqua


DEBUG = env.bool('DJANGO_DEBUG', default=True)
CORS_ORIGIN_WHITELIST = (
    'localhost:3000',
)

# django-debug-toolbar
# ------------------------------------------------------------------------------

MIDDLEWARE_CLASSES += ['debug_toolbar.middleware.DebugToolbarMiddleware', ]
INSTALLED_APPS += ['debug_toolbar', ]

INTERNAL_IPS = ['127.0.0.1', '10.0.2.2', ]

DEBUG_TOOLBAR_CONFIG = {
    'DISABLE_PANELS': [
        'debug_toolbar.panels.redirects.RedirectsPanel',
    ],
    'SHOW_TEMPLATE_CONTEXT': True,
}


# django-extensions
# ------------------------------------------------------------------------------
INSTALLED_APPS += ['django_extensions', ]