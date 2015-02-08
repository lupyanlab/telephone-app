from .base import *


DEBUG = True
TEMPLATE_DEBUG = DEBUG

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Make this unique, and don't share it with anybody.
SECRET_KEY = '79&vz)($@07na+25vw4nb0r^p*6w0j+-x!m)y5p#76tp!gvs_5'

# 3rd-party apps tracking IDs.
INTERCOM_APP_ID = None
GOOGLE_ANALYTICS_TRACKING_ID = None
ADDTHIS_PUBLISHER_ID = None

EMAIL_HOST = 'smtp.example.com'
EMAIL_HOST_USER = 'test'
EMAIL_HOST_PASSWORD = 'test'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

ADMINS = (
    ('Local Admin', 'admin@glucosetracker.net'),
)

MANAGERS = ADMINS

CONTACTS = {
    'support_email': 'support@glucosetracker.net',
    'admin_email': 'admin@glucosetracker.net',
    'info_email': 'info@glucosetracker.net',
}

# For 'subscribers' app
SEND_SUBSCRIBERS_EMAIL_CONFIRMATION = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'glucosetracker',
        'USER': 'glucosetracker',
        'PASSWORD': 'password',
        'HOST': os.environ.get('POSTGRESQL_HOST', 'localhost'),
        'PORT': '',
    }
}

# Django-debug-toolbar config
INSTALLED_APPS += ('debug_toolbar',)
INTERNAL_IPS = (
    '127.0.0.1',
    '192.168.33.1',
    '172.17.42.1',
)
MIDDLEWARE_CLASSES += \
    ('debug_toolbar.middleware.DebugToolbarMiddleware', )

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
    'SHOW_TEMPLATE_CONTEXT': True,
    'HIDE_DJANGO_SQL': False,
}