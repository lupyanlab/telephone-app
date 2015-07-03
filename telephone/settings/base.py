"""
Django settings for telephone project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

from os import environ
from unipath import Path

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'v**w_+36aa+cd%#8%07a59b3&x#k9b%0id+ffr7e3c#8h24%mr'

# Application definition
APP_DIR = Path(__file__).ancestor(2)
PROJ_DIR = APP_DIR.parent

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

    # Third-party apps
    'crispy_forms',

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

STATIC_ROOT = Path(PROJ_DIR, 'static')

STATICFILES_DIRS = (
    Path(APP_DIR, 'telephone/static'),
    Path(APP_DIR, 'grunt/static'),
)

MEDIA_URL = '/media/'

MEDIA_ROOT = Path(PROJ_DIR, 'media')


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

CRISPY_TEMPLATE_PACK = 'bootstrap3'
