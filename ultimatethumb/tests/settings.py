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

MEDIA_ROOT = tempfile.mkdtemp()
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(os.path.dirname(__file__), 'resources', 'static'),
STATIC_URL = '/static/'

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), 'resources', 'templates'),
)
