import os
import tempfile


DEBUG = True

SECRET_KEY = 'testing'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',

    'ultimatethumb',
    'tests.resources.mockapp',
]

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'APP_DIRS': True,
    'DIRS': [os.path.join(os.path.dirname(__file__), 'templates')]
}]


MEDIA_ROOT = tempfile.mkdtemp()
MEDIA_URL = '/media/'

STATICFILES_DIRS = [
    os.path.join(os.path.dirname(__file__), 'resources', 'static'),
]
STATIC_ROOT = tempfile.mkdtemp()
STATIC_URL = '/static/'

ULTIMATETHUMB_ROOT = tempfile.mkdtemp()
ULTIMATETHUMB_URL = '/'

ROOT_URLCONF = 'ultimatethumb.urls'
