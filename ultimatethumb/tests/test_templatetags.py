import os

import pytest
from django.template import Context, Template

from ultimatethumb.tests.factories.mockapp import ImageModelFactory


@pytest.mark.django_db
class TestUltimatethumbTags:
    def test_no_source(self, settings):
        settings.DEBUG = True
        template = Template((
            '{%% load ultimatethumb_tags %%}'
            '{%% ultimatethumb "img" "%s" sizes="100x0" %%}'
        ) % 'static:notexist.file')

        context = Context()
        assert template.render(context) == ''

        assert context['img'] is None

    def test_invalid_source(self, settings):
        settings.DEBUG = True
        template = Template((
            '{%% load ultimatethumb_tags %%}'
            '{%% ultimatethumb "img" "%s" sizes="100x0" %%}'
        ) % 'static:test.txt')

        context = Context()
        assert template.render(context) == ''

        assert context['img'] is None

    def test_static_source(self, settings):
        settings.DEBUG = True
        template = Template((
            '{%% load ultimatethumb_tags %%}'
            '{%% ultimatethumb "img" "%s" sizes="100x0" %%}'
        ) % 'static:50x50-placeholder.png')

        context = Context()
        assert template.render(context) == ''

        assert context['img'][0].source == os.path.join(
            settings.STATICFILES_DIRS[0], '50x50-placeholder.png')

    def test_path_source(self, settings):
        source = ImageModelFactory.create()

        template = Template((
            '{%% load ultimatethumb_tags %%}'
            '{%% ultimatethumb "img" "%s" sizes="100x0" %%}'
        ) % source.file.path)

        context = Context()
        assert template.render(context) == ''

        assert context['img'][0].source == os.path.join(
            settings.MEDIA_ROOT, source.file.name)

    def test_media_source(self, settings):
        source = ImageModelFactory.create()

        template = Template((
            '{%% load ultimatethumb_tags %%}'
            '{%% ultimatethumb "img" "%s" sizes="100x0" %%}'
        ) % source.file.name)

        context = Context()
        assert template.render(context) == ''

        assert context['img'][0].source == os.path.join(
            settings.MEDIA_ROOT, source.file.name)

    def test_crop(self):
        source = ImageModelFactory.create(file__width=210, file__height=100)

        template = Template((
            '{%% load ultimatethumb_tags %%}'
            '{%% ultimatethumb "img" "%s" sizes="200x0" crop=True %%}'
        ) % source.file.path)

        context = Context()
        assert template.render(context) == ''

        assert 'img' in context
        assert len(context['img']) == 1
        assert context['img'][0].options['crop'] is True

    def test_quality(self):
        source = ImageModelFactory.create(file__width=210, file__height=100)

        template = Template((
            '{%% load ultimatethumb_tags %%}'
            '{%% ultimatethumb "img" "%s" sizes="200x0" quality=10 %%}'
        ) % source.file.path)

        context = Context()
        assert template.render(context) == ''

        assert 'img' in context
        assert len(context['img']) == 1
        assert context['img'][0].options['quality'] == 10

    def test_pngquant(self):
        source = ImageModelFactory.create(file__width=210, file__height=100)

        template = Template((
            '{%% load ultimatethumb_tags %%}'
            '{%% ultimatethumb "img" "%s" sizes="200x0" pngquant=10 %%}'
        ) % source.file.path)

        context = Context()
        assert template.render(context) == ''

        assert 'img' in context
        assert len(context['img']) == 1
        assert context['img'][0].options['pngquant'] == 10

    def test_viewport(self):
        source = ImageModelFactory.create(file__width=400, file__height=100)

        template = Template((
            '{%% load ultimatethumb_tags %%}'
            '{%% ultimatethumb "img" "%s" sizes="200:600" %%}'
        ) % source.file.path)

        context = Context()
        assert template.render(context) == ''

        assert 'img' in context
        assert len(context['img']) == 1
        assert context['img'][0].options['size'] == ['200', '0']
        assert context['img'][0].options['viewport'] == ['600', '0']

    def test_oversize(self):
        source = ImageModelFactory.create(file__width=210, file__height=100)

        template = Template((
            '{%% load ultimatethumb_tags %%}'
            '{%% ultimatethumb "img" "%s" sizes="100x0,200x0,300x0,400x0" retina=False %%}'
        ) % source.file.path)

        context = Context()
        assert template.render(context) == ''

        assert 'img' in context
        assert len(context['img']) == 3
        assert context['img'][0].requested_size.width == '100'
        assert context['img'][0].requested_size.height == '0'
        assert context['img'][1].requested_size.width == '200'
        assert context['img'][1].requested_size.height == '0'
        assert context['img'][2].requested_size.width == '210'
        assert context['img'][2].requested_size.height == '100'

    def test_oversize_upscale(self):
        source = ImageModelFactory.create(file__width=210, file__height=100)

        template = Template((
            '{%% load ultimatethumb_tags %%}'
            '{%% ultimatethumb "img" "%s" sizes="100x0,200x0,300x0,400x0" upscale=True %%}'
        ) % source.file.path)

        context = Context()
        assert template.render(context) == ''

        assert 'img' in context
        assert len(context['img']) == 4
        assert context['img'][0].requested_size.width == '100'
        assert context['img'][0].requested_size.height == '0'
        assert context['img'][1].requested_size.width == '200'
        assert context['img'][1].requested_size.height == '0'
        assert context['img'][2].requested_size.width == '300'
        assert context['img'][2].requested_size.height == '0'
        assert context['img'][3].requested_size.width == '400'
        assert context['img'][3].requested_size.height == '0'

    def test_retina(self):
        source = ImageModelFactory.create(file__width=210, file__height=100)

        template = Template((
            '{%% load ultimatethumb_tags %%}'
            '{%% ultimatethumb "img" "%s" sizes="100x0,200x0,300x0,400x0" %%}'
        ) % source.file.path)

        context = Context()
        assert template.render(context) == ''

        assert 'img' in context
        assert len(context['img']) == 2
        assert context['img'][0].requested_size.width == '100'
        assert context['img'][0].requested_size.height == '0'
        assert context['img'][0].url is not None
        assert context['img'][0].url_2x is not None
        assert context['img'][1].requested_size.width == '105'
        assert context['img'][1].requested_size.height == '50'
        assert context['img'][1].url is not None
        assert context['img'][1].url_2x is not None

    def test_retina_disabled(self):
        source = ImageModelFactory.create(file__width=210, file__height=100)

        template = Template((
            '{%% load ultimatethumb_tags %%}'
            '{%% ultimatethumb "img" "%s" sizes="100x0,200x0,300x0,400x0" retina=False %%}'
        ) % source.file.path)

        context = Context()
        assert template.render(context) == ''

        assert 'img' in context
        assert len(context['img']) == 3
        assert context['img'][0].requested_size.width == '100'
        assert context['img'][0].requested_size.height == '0'
        assert context['img'][0].url is not None
        assert context['img'][0].url_2x is None
        assert context['img'][1].requested_size.width == '200'
        assert context['img'][1].requested_size.height == '0'
        assert context['img'][1].url is not None
        assert context['img'][1].url_2x is None
        assert context['img'][2].requested_size.width == '210'
        assert context['img'][2].requested_size.height == '100'
        assert context['img'][2].url is not None
