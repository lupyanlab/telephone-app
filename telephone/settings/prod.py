from .base import *

DEBUG = False
TEMPLATE_DEBUG = False
ALLOWED_HOSTS = ['grunt.pedmiston.xyz', ]

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
