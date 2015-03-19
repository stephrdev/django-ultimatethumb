import pytest

from django.core.exceptions import ImproperlyConfigured

from ultimatethumb.storage import ThumbnailFileSystemStorage, thumbnail_storage


def test_lazy_thumbnail_storage():
    assert isinstance(thumbnail_storage, ThumbnailFileSystemStorage) is True


class TestThumbnailFileSystemStorage:
    def test_empty_root(self, settings):
        settings.ULTIMATETHUMB_ROOT = ''

        with pytest.raises(ImproperlyConfigured):
            ThumbnailFileSystemStorage()

    def test_empty_url(self, settings):
        settings.ULTIMATETHUMB_URL = ''

        with pytest.raises(ImproperlyConfigured):
            ThumbnailFileSystemStorage()

    def test_settings(self, settings):
        settings.ULTIMATETHUMB_ROOT = '/path/to/thumbs/'
        settings.ULTIMATETHUMB_URL = '/url/to/thumbs/'

        storage = ThumbnailFileSystemStorage()
        assert storage.path('test.test') == '/path/to/thumbs/test.test'
        assert storage.url('test.test') == '/url/to/thumbs/test.test'

    def test_arguments(self, settings):
        settings.ULTIMATETHUMB_ROOT = '/path/to/settingsthumbs/'
        settings.ULTIMATETHUMB_URL = '/url/to/settingsthumbs/'

        storage = ThumbnailFileSystemStorage(
            location='/path/to/thumbs/', base_url='/url/to/thumbs/')
        assert storage.path('test.test') == '/path/to/thumbs/test.test'
        assert storage.url('test.test') == '/url/to/thumbs/test.test'
