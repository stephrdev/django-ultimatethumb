from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import FileSystemStorage, get_storage_class
from django.utils.functional import LazyObject

from .utils import get_domain_url


class ThumbnailFileSystemStorage(FileSystemStorage):

    def __init__(self, location=None, base_url=None, *args, **kwargs):
        if location is None:
            location = getattr(settings, 'ULTIMATETHUMB_ROOT', None) or None
        if base_url is None:
            base_url = getattr(settings, 'ULTIMATETHUMB_URL', None)

        if not location:
            raise ImproperlyConfigured('ULTIMATETHUMB_ROOT not set.')

        if not base_url:
            raise ImproperlyConfigured('ULTIMATETHUMB_URL not set.')

        super(ThumbnailFileSystemStorage, self).__init__(
            location, get_domain_url(base_url), *args, **kwargs)


class ThumbnailStorage(LazyObject):

    def _setup(self):
        self._wrapped = get_storage_class(
            getattr(
                settings,
                'ULTIMATETHUMB_STORAGE',
                'ultimatethumb.storage.ThumbnailFileSystemStorage'
            )
        )()

thumbnail_storage = ThumbnailStorage()
