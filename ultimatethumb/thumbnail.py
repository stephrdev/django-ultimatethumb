import os
from collections import namedtuple

from barbeque.commands.imaging import GmConvertCommand
from barbeque.files import MoveableNamedTemporaryFile
from django.core.urlresolvers import reverse
from django.utils.datastructures import SortedDict

from .storage import thumbnail_storage
from .utils import (
    get_thumb_data, get_thumb_name, factor_size, get_size_for_path)


Size = namedtuple('Size', ('width', 'height'))


class Thumbnail(object):
    def __init__(self, source, opts):
        self.source = source
        self.options = opts

    def __repr__(self):
        return '<Thumbnail: {0} {1}>'.format(
            self.source,
            ' '.join(['{0}={1}'.format(k, self.options[k]) for k in sorted(self.options)])
        )

    @classmethod
    def from_name(cls, name):
        return Thumbnail(*get_thumb_data(name))

    def get_name(self):
        return get_thumb_name(self.source, **self.options)

    @property
    def size(self):
        return self.get_size()

    @property
    def url(self):
        return reverse('thumbnail', kwargs={'name': self.get_name()})

    @property
    def url_2x(self):
        return reverse('thumbnail-factor', kwargs={'factor': 2, 'name': self.get_name()})

    @property
    def requested_size(self):
        return Size(*self.options['size'])

    def exists(self, factor=1):
        return os.path.exists(self.get_storage_path(factor, generate=False))

    def get_storage_url(self, factor=1):
        return thumbnail_storage.url(self.get_storage_name(factor))

    def get_storage_path(self, factor=1, generate=True):
        if generate and not self.exists(factor):
            self.generate(factor)

        return thumbnail_storage.path(self.get_storage_name(factor))

    def get_size(self, factor=1):
        return Size(*get_size_for_path(self.get_storage_path(factor)))

    def get_storage_name(self, factor=1):
        name = self.get_name()
        if factor != 1:
            name = os.path.join('{0}x'.format(factor), name)
        return name

    def generate(self, factor=1):
        thumb_name = self.get_storage_name(factor)

        tmpfile = MoveableNamedTemporaryFile(thumb_name)
        resizer = GmConvertCommand(
            infile='"{0}"'.format(self.source),
            outfile=tmpfile.temporary_file_path(),
            options=self.get_gm_options(factor)
        )
        assert resizer.execute()

        thumbnail_storage.save(thumb_name, tmpfile)

        return True

    def get_gm_options(self, factor=1):
        gm_options = SortedDict()

        # Remove any icc profiles to avoid problems.
        gm_options['+profile'] = '"*"'

        gm_options['resize'] = '{0}x{1}{2}'.format(
            factor_size(self.options['size'][0], factor),
            factor_size(self.options['size'][1], factor),
            '' if self.options.get('upscale', False) else '>'
        )

        if self.options.get('crop', False):
            gm_options['gravity'] = 'Center'
            gm_options['crop'] = '{0}x{1}'.format(
                factor_size(self.options['size'][0], factor),
                factor_size(self.options['size'][1], factor)
            )

        if 'quality' in self.options:
            gm_options['quality'] = self.options['quality']

        return gm_options
