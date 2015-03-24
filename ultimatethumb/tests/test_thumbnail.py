import os

import mock
import pytest
from django.core.cache import cache

from ultimatethumb.storage import thumbnail_storage
from ultimatethumb.tests.factories.mockapp import ImageModelFactory
from ultimatethumb.thumbnail import Size, Thumbnail


@pytest.mark.django_db
class TestThumbnail:
    def setup(self):
        cache.clear()

    def teardown(self):
        cache.clear()

    def test_repr(self):
        thumbnail = Thumbnail('test.jpg', {'size': ['100', '100'], 'upscale': False})
        assert repr(thumbnail) == (
            "<Thumbnail: test.jpg crop=False size=['100', '100'] upscale=False>")

    def test_invalid_opts(self):
        with pytest.raises(ValueError) as exc:
            Thumbnail('test.jpg', {})

        assert '`size` is required' in str(exc.value)

    def test_get_name(self):
        thumbnail = Thumbnail('test.jpg', {'size': ['100', '100']})
        assert thumbnail.get_name() == '48382ea502faf93772a5b07f7d8a590f01d0f15b/test.jpg'

    def test_from_name(self):
        thumbnail = Thumbnail('test.jpg', {'size': ['100', '100']})
        thumbnail2 = Thumbnail.from_name(thumbnail.get_name())

        assert thumbnail.source == thumbnail2.source
        assert thumbnail.options == thumbnail2.options

    def test_get_estimated_size(self):
        image = ImageModelFactory.create()
        thumbnail = Thumbnail(image.file.path, {'size': ['50', '50']})

        size = thumbnail.get_estimated_size()
        assert size.width == 25
        assert size.height == 50

        # Test property
        assert thumbnail.size == size

    def test_get_size(self):
        image = ImageModelFactory.create()
        thumbnail = Thumbnail(image.file.path, {'size': ['50', '50']})

        size = thumbnail.get_size()
        assert size.width == 25
        assert size.height == 50

    def test_url(self):
        thumbnail = Thumbnail('test.jpg', {'size': ['100', '100']})
        assert thumbnail.url == (
            '/48382ea502faf93772a5b07f7d8a590f01d0f15b/test.jpg')

    def test_url_2x(self):
        thumbnail = Thumbnail('test.jpg', {'size': ['100', '100']})
        assert thumbnail.url_2x == (
            '/2x/48382ea502faf93772a5b07f7d8a590f01d0f15b/test.jpg')

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

    def test_gm_options_crop(self):
        image = ImageModelFactory.create()
        thumbnail = Thumbnail(image.file.path, {'size': ['100', '50'], 'crop': False})
        assert 'gravity' not in thumbnail.get_gm_options()
        assert 'crop' not in thumbnail.get_gm_options()

        thumbnail = Thumbnail(image.file.path, {'size': ['100', '50'], 'crop': True})
        assert list(thumbnail.get_gm_options().items()) == [
            ('+profile', '"*"'),
            ('resize', '50x25^'),
            ('gravity', 'Center'),
            ('crop', '50x25+0+0')
        ]

    def test_gm_options_quality(self):
        image = ImageModelFactory.create()
        thumbnail = Thumbnail(image.file.path, {'size': ['100', '50'], 'quality': 5})
        assert thumbnail.get_gm_options()['quality'] == 5

    @pytest.mark.parametrize('input_size,thumb_size,upscale,crop,expected', [
        ((100, 200), (600, 300), True, True, ('600x300^', '600x300+0+0')),
        ((100, 200), (600, 300), True, False, ('150x300', None)),
        ((100, 200), (600, 300), False, True, ('100x50^', '100x50+0+0')),
        ((100, 200), (600, 300), False, False, ('100x200>', None)),

        ((100, 200), (300, 600), True, True, ('300x600^', '300x600+0+0')),
        ((100, 200), (300, 600), True, False, ('300x600', None)),
        ((100, 200), (300, 600), False, True, ('100x200^', '100x200+0+0')),
        ((100, 200), (300, 600), False, False, ('100x200>', None)),

        ((200, 400), (100, 50), True, True, ('100x50^', '100x50+0+0')),
        ((200, 400), (100, 50), True, False, ('25x50', None)),
        ((200, 400), (100, 50), False, True, ('100x50^', '100x50+0+0')),
        ((200, 400), (100, 50), False, False, ('25x50>', None)),

        ((200, 400), (50, 100), True, True, ('50x100^', '50x100+0+0')),
        ((200, 400), (50, 100), True, False, ('50x100', None)),
        ((200, 400), (50, 100), False, True, ('50x100^', '50x100+0+0')),
        ((200, 400), (50, 100), False, False, ('50x100>', None)),

        ((100, 200), (600, 200), True, True, ('600x200^', '600x200+0+0')),
        ((100, 200), (600, 200), True, False, ('100x200', None)),
        ((100, 200), (600, 200), False, True, ('100x33^', '100x33+0+0')),
        ((100, 200), (600, 200), False, False, ('100x200>', None)),

        ((100, 200), (200, 600), True, True, ('200x600^', '200x600+0+0')),
        ((100, 200), (200, 600), True, False, ('200x400', None)),
        ((100, 200), (200, 600), False, True, ('67x200^', '67x200+0+0')),
        ((100, 200), (200, 600), False, False, ('100x200>', None)),
    ])
    def test_gm_options_sizes(self, input_size, thumb_size, upscale, crop, expected):
        image = ImageModelFactory.create(
            file__width=input_size[0], file__height=input_size[1])

        instance = Thumbnail(image.file.path, {
            'size': (str(thumb_size[0]), str(thumb_size[1])),
            'upscale': upscale,
            'crop': crop
        })

        assert_error = '{0} -> {1} (upscale: {3} crop: {2})'.format(
            input_size,
            thumb_size,
            crop,
            upscale
        )

        options = instance.get_gm_options()
        assert options.get('resize', None) == expected[0], assert_error
        assert options.get('crop', None) == expected[1], assert_error

    @pytest.mark.parametrize('input_size,thumb_size,upscale,crop,expected', [
        ((100, 200), (200, 100), True, True, (200, 100)),
        ((100, 200), (200, 100), False, True, (100, 50)),
        ((100, 200), (200, 100), True, False, (50, 100)),
        ((100, 200), (200, 100), False, False, (50, 100)),
        ((100, 200), (100, 100), True, True, (100, 100)),
        ((100, 200), (100, 100), False, True, (100, 100)),
        ((100, 200), (100, 100), True, False, (50, 100)),
        ((100, 200), (100, 100), False, False, (50, 100)),
        ((100, 200), (50, 100), True, True, (50, 100)),
        ((100, 200), (50, 100), False, True, (50, 100)),
        ((100, 200), (50, 100), True, False, (50, 100)),
        ((100, 200), (50, 100), False, False, (50, 100)),
        ((100, 200), (50, 50), True, True, (50, 50)),
        ((100, 200), (50, 50), False, True, (50, 50)),
        ((100, 200), (50, 50), True, False, (25, 50)),
        ((100, 200), (50, 50), False, False, (25, 50)),
        ((100, 200), (200, 400), True, True, (200, 400)),
        ((100, 200), (200, 400), False, True, (100, 200)),
        ((100, 200), (200, 400), True, False, (200, 400)),
        ((100, 200), (200, 400), False, False, (100, 200)),
        ((100, 200), (400, 400), True, True, (400, 400)),
        ((100, 200), (400, 400), False, True, (100, 100)),
        ((100, 200), (400, 400), True, False, (200, 400)),
        ((100, 200), (400, 400), False, False, (100, 200)),
        ((100, 200), (200, 200), True, True, (200, 200)),
        ((100, 200), (200, 200), False, True, (100, 100)),
        ((100, 200), (200, 200), True, False, (100, 200)),
        ((100, 200), (200, 200), False, False, (100, 200)),
        ((100, 200), (200, 400), True, True, (200, 400)),
        ((100, 200), (200, 400), False, True, (100, 200)),
        ((100, 200), (200, 400), True, False, (200, 400)),
        ((100, 200), (200, 400), False, False, (100, 200)),
        ((100, 200), (400, 400), True, True, (400, 400)),
        ((100, 200), (400, 400), False, True, (100, 100)),
        ((100, 200), (400, 400), True, False, (200, 400)),
        ((100, 200), (400, 400), False, False, (100, 200)),
        ((100, 200), (50, 300), True, True, (50, 300)),
        ((100, 200), (50, 300), False, True, (33, 200)),
        ((100, 200), (50, 300), True, False, (50, 100)),
        ((100, 200), (50, 300), False, False, (50, 100)),
        ((100, 200), (300, 50), True, True, (300, 50)),
        ((100, 200), (300, 50), False, True, (100, 17)),
        ((100, 200), (300, 50), True, False, (25, 50)),
        ((100, 200), (300, 50), False, False, (25, 50)),
        ((100, 200), (200, 0), True, True, (200, 400)),
        ((100, 200), (200, 0), False, True, (100, 200)),
        ((100, 200), (200, 0), True, False, (200, 400)),
        ((100, 200), (200, 0), False, False, (100, 200)),
        ((100, 200), (50, 0), True, True, (50, 100)),
        ((100, 200), (50, 0), False, True, (50, 100)),
        ((100, 200), (50, 0), True, False, (50, 100)),
        ((100, 200), (50, 0), False, False, (50, 100)),
        ((100, 200), (100, 0), True, True, (100, 200)),
        ((100, 200), (100, 0), False, True, (100, 200)),
        ((100, 200), (100, 0), True, False, (100, 200)),
        ((100, 200), (100, 0), False, False, (100, 200)),
        ((100, 200), (200, 0), True, True, (200, 400)),
        ((100, 200), (200, 0), False, True, (100, 200)),
        ((100, 200), (200, 0), True, False, (200, 400)),
        ((100, 200), (200, 0), False, False, (100, 200)),
        ((100, 200), (300, 0), True, True, (300, 600)),
        ((100, 200), (300, 0), False, True, (100, 200)),
        ((100, 200), (300, 0), True, False, (300, 600)),
        ((100, 200), (300, 0), False, False, (100, 200)),
        ((100, 200), (400, 0), True, True, (400, 800)),
        ((100, 200), (400, 0), False, True, (100, 200)),
        ((100, 200), (400, 0), True, False, (400, 800)),
        ((100, 200), (400, 0), False, False, (100, 200)),
        ((100, 200), (0, 50), True, True, (25, 50)),
        ((100, 200), (0, 50), False, True, (25, 50)),
        ((100, 200), (0, 50), True, False, (25, 50)),
        ((100, 200), (0, 50), False, False, (25, 50)),
        ((100, 200), (0, 100), True, True, (50, 100)),
        ((100, 200), (0, 100), False, True, (50, 100)),
        ((100, 200), (0, 100), True, False, (50, 100)),
        ((100, 200), (0, 100), False, False, (50, 100)),
        ((100, 200), (0, 200), True, True, (100, 200)),
        ((100, 200), (0, 200), False, True, (100, 200)),
        ((100, 200), (0, 200), True, False, (100, 200)),
        ((100, 200), (0, 200), False, False, (100, 200)),
        ((100, 200), (0, 300), True, True, (150, 300)),
        ((100, 200), (0, 300), False, True, (100, 200)),
        ((100, 200), (0, 300), True, False, (150, 300)),
        ((100, 200), (0, 300), False, False, (100, 200)),
        ((100, 200), (0, 400), True, True, (200, 400)),
        ((100, 200), (0, 400), False, True, (100, 200)),
        ((100, 200), (0, 400), True, False, (200, 400)),
        ((100, 200), (0, 400), False, False, (100, 200)),
        ((100, 200), (75, 100), True, True, (75, 100)),
        ((100, 200), (75, 100), False, True, (75, 100)),
        ((100, 200), (75, 100), True, False, (50, 100)),
        ((100, 200), (75, 100), False, False, (50, 100)),
        ((100, 200), (0, '75%'), True, True, (75, 150)),
        ((100, 200), ('50%', 0), True, True, (50, 100)),
    ])
    def test_estimated_size(self, input_size, thumb_size, upscale, crop, expected):
        image = ImageModelFactory.create(
            file__width=input_size[0], file__height=input_size[1])

        instance = Thumbnail(image.file.path, {
            'size': (str(thumb_size[0]), str(thumb_size[1])),
            'upscale': upscale,
            'crop': crop
        })
        assert instance.get_estimated_size() == Size(*expected), (
            '{0} -> {1} (upscale: {3} crop: {2})'.format(
                input_size,
                thumb_size,
                crop,
                upscale
            ))
