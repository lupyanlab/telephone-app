"""
Django settings for telephone project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

from os import environ
from unipath import Path
BASE_DIR = Path(__file__).ancestor(3)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'v**w_+36aa+cd%#8%07a59b3&x#k9b%0id+ffr7e3c#8h24%mr'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

APP_DIR = Path(BASE_DIR, 'telephone')

TEMPLATE_DIRS = (
    Path(APP_DIR, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Local apps
    'grunt',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'telephone.urls'

WSGI_APPLICATION = 'telephone.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'telephone',
        'USER': 'telephone',
        'PASSWORD': 'password',
        'HOST': environ.get('POSTGRESQL_HOST', 'localhost'),
        'PORT': '',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = Path(BASE_DIR, 'static')  # will likely vary

STATICFILES_DIRS = (
    Path(APP_DIR, 'telephone', 'static'),
    Path(APP_DIR, 'grunt', 'static'),
)

MEDIA_URL = '/media/'

MEDIA_ROOT = Path(BASE_DIR, 'media')  # will likely vary

# Logging
# https://docs.djangoproject.com/en/1.7/topics/logging/

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s  [%(name)s:%(lineno)s]  %(levelname)s - %(message)s',
        },
        'simple': {
            'format': '%(levelname)s %(message)s',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        }
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        }
    },
    'loggers': {
        # Silence SuspiciousOperation.DisallowedHost exception ('Invalid
        # HTTP_HOST' header messages). Set the handler to 'null' so we don't
        # get those annoying emails.
        'django.security.DisallowedHost': {
            'handlers': ['null'],
            'propagate': False,
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        '': {
            'handlers': ['console', ],
            'level': 'INFO',
        }
    }
}

# Testing
# http://model-mommy.readthedocs.org/en/latest/how_mommy_behaves.html#custom-fields

import string
from random import choice

def gen_small_str(max_length, percentage = 0.75):
    """ Generate a random string at specified percentage of max length """
    new_length = int(max_length * percentage)
    result = list(choice(string.ascii_letters) for _ in range(new_length))
    return u''.join(result)
gen_small_str.required = ['max_length']

MOMMY_CUSTOM_FIELDS_GEN = {
    'django.db.models.fields.CharField': gen_small_str,
}
