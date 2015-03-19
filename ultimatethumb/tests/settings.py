import os
import tempfile


DEBUG = TEMPLATE_DEBUG = True

SECRET_KEY = 'testing'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

INSTALLED_APPS = (
    'ultimatethumb',
    'ultimatethumb.tests.resources.mockapp',
)

MIDDLEWARE_CLASSES = []

ROOT_URLCONF = 'ultimatethumb.urls'

MEDIA_ROOT = tempfile.mkdtemp()
MEDIA_URL = '/media/'

STATICFILES_DIRS = [
    os.path.join(os.path.dirname(__file__), 'resources', 'static'),
]
STATIC_URL = '/static/'

ULTIMATETHUMB_ROOT = tempfile.mkdtemp()
ULTIMATETHUMB_URL = '/'

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), 'resources', 'templates'),
)
