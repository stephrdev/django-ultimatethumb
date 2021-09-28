from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import FileSystemStorage, get_storage_class
from django.utils.functional import LazyObject

from .utils import get_domain_url


class ThumbnailFileSystemStorage(FileSystemStorage):
    """
    Extended FileSystemStorage from Django which uses ULTIMATETHUMB_* settings
    to initialize storage backend.

    This storage is used to handle the generated files.
    """

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
            location, get_domain_url(base_url), *args, **kwargs
        )


class ThumbnailStorage(LazyObject):
    """
    Lazy class to defer the initialization of the thumbnail_storage to give
    settings a chance to override the used storage backend.
    """

    def _setup(self):
        self._wrapped = get_storage_class(
            getattr(
                settings,
                'ULTIMATETHUMB_STORAGE',
                'ultimatethumb.storage.ThumbnailFileSystemStorage',
            )
        )()


thumbnail_storage = ThumbnailStorage()
