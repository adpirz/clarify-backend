"""
Django settings for clarify_backend project.

Generated by 'django-admin startproject' using Django 1.8.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import environ

env = environ.Env()
environ.Env.read_env()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ANONYMIZE_STUDENTS = True

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'xc*okanrxohxi-s^yae6l=ve^-1no7ga$)r=-(8#c)#b8ro@+u'

# Application definition

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
]

APP_DOMAIN = 'app.clarify.school'
API_DOMAIN = 'api.clarify.school'

THIRD_PARTY_APPS = [
    'corsheaders',
    'django_extensions',
]

CLARIFY_APPS = [
    'sis_mirror.apps.SisMirrorConfig',
    'deltas.apps.DeltasConfig',
    'clarify.apps.ClarifyConfig'
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + CLARIFY_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ORIGIN_ALLOW_ALL = False

ROOT_URLCONF = 'clarify_backend.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'clarify_backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': env.db('DATABASE_URL', default="postgres:///clarify"),
    'cache': {
        'NAME': env('CACHE_NAME', default='clarifycache'),
        'ENGINE': 'django.db.backends.postgresql',
        'USER': env('CACHE_USER', default='postgres'),
        'PASSWORD': env('CACHE_PASSWORD', default=None),
        'HOST': env('CACHE_HOST', default=None),
        'PORT': env('CACHE_PORT', default=5432)
    }

}

DATABASE_ROUTERS = ['sis_mirror.routers.MirrorRouter']

# Include schema in sis_mirror models db_table reference
# db_table references will be <schema>.<table> (except for 'public' schema)
SIS_MIRROR_WITH_SCHEMA = env.bool('SIS_MIRROR_WITH_SCHEMA', default=False)

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = env.bool('USE_TZ', default=True)
IMPERSONATION = env.bool('IMPERSONATION', default=False)
DEBUG = env.bool('DEBUG', default=False)


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'

# Silence an FK warning from sis_mirror which is a necessary field
SILENCED_SYSTEM_CHECKS = ['fields.W342']

# Google auth
GOOGLE_CLIENT_ID = env('GOOGLE_CLIENT_ID', default=None)
GOOGLE_CLIENT_SECRET = env('GOOGLE_CLIENT_SECRET', default=None)

# Clever
CLEVER_CLIENT_ID = env('CLEVER_CLIENT_ID', default=None)
CLEVER_CLIENT_SECRET = env('CLEVER_CLIENT_SECRET', default=None)
CLEVER_REDIRECT_URL = env('CLEVER_REDIRECT_URL', default=None)

# Sendgrid
SENDGRID_API_KEY = env('SENDGRID_API_KEY', default=None)

# Password reset debug email
RESET_DEBUG_EMAIL = env('RESET_DEBUG_EMAIL', default=None)