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
        template.render(context)

        assert context['img'] is None

    def test_invalid_source(self, settings):
        settings.DEBUG = True
        template = Template((
            '{%% load ultimatethumb_tags %%}'
            '{%% ultimatethumb "img" "%s" sizes="100x0" %%}'
        ) % 'static:robots.txt')

        context = Context()
        template.render(context)

        assert context['img'] is None

    def test_static_source(self, settings):
        settings.DEBUG = True
        template = Template((
            '{%% load ultimatethumb_tags %%}'
            '{%% ultimatethumb "img" "%s" sizes="100x0" %%}'
        ) % 'static:50x50-placeholder.png')

        context = Context()
        template.render(context)

        assert context['img'][0].source == os.path.join(
            settings.STATICFILES_DIRS[0], '50x50-placeholder.png')

    def test_path_source(self, settings):
        source = ImageModelFactory.create()

        template = Template((
            '{%% load ultimatethumb_tags %%}'
            '{%% ultimatethumb "img" "%s" sizes="100x0" %%}'
        ) % source.file.path)

        context = Context()
        template.render(context)

        assert context['img'][0].source == os.path.join(
            settings.MEDIA_ROOT, source.file.name)

    def test_media_source(self, settings):
        source = ImageModelFactory.create()

        template = Template((
            '{%% load ultimatethumb_tags %%}'
            '{%% ultimatethumb "img" "%s" sizes="100x0" %%}'
        ) % source.file.name)

        context = Context()
        template.render(context)

        assert context['img'][0].source == os.path.join(
            settings.MEDIA_ROOT, source.file.name)

    def test_oversize(self):
        source = ImageModelFactory.create(file__width=210, file__height=100)

        template = Template((
            '{%% load ultimatethumb_tags %%}'
            '{%% ultimatethumb "img" "%s" sizes="100x0,200x0,300x0,400x0" retina=False %%}'
        ) % source.file.path)

        context = Context()
        template.render(context)

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
        template.render(context)

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
        template.render(context)

        assert 'img' in context
        assert len(context['img']) == 2
        assert context['img'][0].requested_size.width == '100'
        assert context['img'][0].requested_size.height == '0'
        assert context['img'][1].requested_size.width == '105'
        assert context['img'][1].requested_size.height == '50'
