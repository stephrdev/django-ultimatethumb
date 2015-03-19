import os

import mock
import pytest
from django.core.cache import cache

from ultimatethumb.thumbnail import Thumbnail
from ultimatethumb.storage import thumbnail_storage

from ultimatethumb.tests.factories.mockapp import ImageModelFactory


@pytest.mark.django_db
class TestThumbnail:
    def setup(self):
        cache.clear()

    def test_repr(self):
        thumbnail = Thumbnail('test.jpg', {'size': ['100', '100'], 'upscale': False})
        assert repr(thumbnail) == "<Thumbnail: test.jpg size=['100', '100'] upscale=False>"

    def test_get_name(self):
        thumbnail = Thumbnail('test.jpg', {'size': ['100', '100']})
        assert thumbnail.get_name() == 'c1e39649c351ee292b76db4432459603a0a0e46c/test.jpg'

    def test_from_name(self):
        thumbnail = Thumbnail('test.jpg', {'size': ['100', '100']})
        thumbnail2 = Thumbnail.from_name(thumbnail.get_name())

        assert thumbnail.source == thumbnail2.source
        assert thumbnail.options == thumbnail2.options

    def test_get_size(self):
        image = ImageModelFactory.create()
        thumbnail = Thumbnail(image.file.path, {'size': ['50', '50']})

        size = thumbnail.get_size()
        assert size.width == 25
        assert size.height == 50

        # Test property
        assert thumbnail.size == size

    def test_url(self):
        thumbnail = Thumbnail('test.jpg', {'size': ['100', '100']})
        assert thumbnail.url == (
            '/c1e39649c351ee292b76db4432459603a0a0e46c/test.jpg')

    def test_url_2x(self):
        thumbnail = Thumbnail('test.jpg', {'size': ['100', '100']})
        assert thumbnail.url_2x == (
            '/2x/c1e39649c351ee292b76db4432459603a0a0e46c/test.jpg')

    def test_requested_size(self):
        thumbnail = Thumbnail('test.jpg', {'size': ['100', '50']})
        assert thumbnail.requested_size.width == '100'
        assert thumbnail.requested_size.height == '50'

    @mock.patch('ultimatethumb.thumbnail.Thumbnail.generate')
    def test_exists_dont_generate(self, generate_mock):
        image = ImageModelFactory.create()
        thumbnail = Thumbnail(image.file.path, {'size': ['50', '50']})

        assert thumbnail.exists() is False
        assert generate_mock.called is False

    def test_exists(self):
        image = ImageModelFactory.create()
        thumbnail = Thumbnail(image.file.path, {'size': ['50', '50']})
        assert thumbnail.exists() is False
        thumbnail.generate()
        assert thumbnail.exists() is True

    def test_storage_url(self):
        thumbnail = Thumbnail('test.jpg', {'size': ['50', '50']})
        assert thumbnail.get_storage_url() == os.path.join(
            thumbnail_storage.base_url, thumbnail.get_name())

    def test_storage_path(self):
        image = ImageModelFactory.create()
        thumbnail = Thumbnail(image.file.path, {'size': ['50', '50']})
        assert thumbnail.get_storage_path() == os.path.join(
            thumbnail_storage.location, thumbnail.get_name())

    def test_storage_name(self):
        thumbnail = Thumbnail('test.jpg', {'size': ['100', '50']})
        assert thumbnail.get_storage_name() == thumbnail.get_name()

    def test_storage_name_factored(self):
        thumbnail = Thumbnail('test.jpg', {'size': ['100', '50']})
        assert thumbnail.get_storage_name(2) == os.path.join('2x', thumbnail.get_name())

    def test_gm_options(self):
        thumbnail = Thumbnail('test.jpg', {'size': ['100', '50']})
        assert list(thumbnail.get_gm_options().items()) == [
            ('+profile', '"*"'), ('resize', '100x50>')]

    def test_gm_options_upscale(self):
        thumbnail = Thumbnail('test.jpg', {'size': ['100', '50'], 'upscale': True})
        assert list(thumbnail.get_gm_options().items()) == [
            ('+profile', '"*"'), ('resize', '100x50')]

    def test_gm_options_crop(self):
        thumbnail = Thumbnail('test.jpg', {'size': ['100', '50'], 'crop': True})
        assert list(thumbnail.get_gm_options().items()) == [
            ('+profile', '"*"'),
            ('resize', '100x50>'),
            ('gravity', 'Center'),
            ('crop', '100x50')
        ]

    def test_gm_options_quality(self):
        thumbnail = Thumbnail('test.jpg', {'size': ['100', '50'], 'quality': 5})
        assert list(thumbnail.get_gm_options().items()) == [
            ('+profile', '"*"'), ('resize', '100x50>'), ('quality', 5)]
