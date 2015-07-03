from .base import *

DEBUG = True
TEMPLATE_DEBUG = True
ALLOWED_HOSTS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'telephone',
        'USER': 'telephone',
        'PASSWORD': 'telephonepass',
        'HOST': environ.get('POSTGRESQL_HOST', 'localhost'),
        'PORT': '',
    },
}
