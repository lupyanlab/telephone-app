from .base import *

DEBUG = True
TEMPLATE_DEBUG = True
ALLOWED_HOSTS = []

DATABASES = {
    'default': {
        'sqlite': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': Path(BASE_DIR, 'telephone.sqlite3'),
        }
    }
}
