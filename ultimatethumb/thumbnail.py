import os
from collections import OrderedDict, namedtuple

from barbeque.commands.imaging import GmConvertCommand
from barbeque.files import MoveableNamedTemporaryFile
from django.conf import settings

from .commands import PngquantCommand
from .storage import thumbnail_storage
from .utils import build_url, factor_size, get_size_for_path, get_thumb_data, get_thumb_name


Size = namedtuple('Size', ('width', 'height'))


class Thumbnail(object):
    def __init__(self, source, opts):
        self.source = source

        if 'size' not in opts:
            raise ValueError('`size` is required but missing in thumbnail options')

        self.options = {
            'crop': False,
            'upscale': False,
            'factor2x': True,
            'quality': getattr(settings, 'ULTIMATETHUMB_GRAPHICSMAGICK_QUALITY', 90),
            'pngquant': getattr(settings, 'ULTIMATETHUMB_PNGQUANT_QUALITY', None),
        }
        self.options.update(opts)

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
        return self.get_estimated_size()

    @property
    def url(self):
        return build_url(self.get_name())

    @property
    def url_2x(self):
        return build_url(self.get_name(), 2) if self.options['factor2x'] else None

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

    def get_estimated_size(self):
        source_size = get_size_for_path(self.source)
        thumb_size = (self.options['size'][0], self.options['size'][1])
        source_width, source_height = source_size

        thumb_width, thumb_height = thumb_size
        if type(thumb_width) is not int:
            if thumb_width[-1] == '%':
                thumb_width = source_width * int(thumb_width[:-1]) / 100.0
            else:
                thumb_width = int(thumb_width)

        if type(thumb_height) is not int:
            if thumb_height[-1] == '%':
                thumb_height = source_height * int(thumb_height[:-1]) / 100.0
            else:
                thumb_height = int(thumb_height)

        # From now on, we calculate with float.
        thumb_width = float(thumb_width)
        thumb_height = float(thumb_height)

        if not thumb_width:
            thumb_width = thumb_height * source_width / source_height

        if not thumb_height:
            thumb_height = thumb_width * source_height / source_width

        width_scale = thumb_width / source_size[0]
        height_scale = thumb_height / source_size[1]

        if self.options['crop']:
            if not self.options['upscale']:
                thumb_ratio = max(width_scale, height_scale, 1)
                thumb_width = thumb_width / thumb_ratio
                thumb_height = thumb_height / thumb_ratio

        else:
            thumb_ratio = min(width_scale, height_scale)
            if not self.options['upscale']:
                thumb_ratio = min(thumb_ratio, 1)

            thumb_width = source_width * thumb_ratio
            thumb_height = source_height * thumb_ratio

        return Size(int(round(thumb_width)), int(round(thumb_height)))

    def get_storage_name(self, factor=1):
        name = self.get_name()
        if factor != 1:
            name = os.path.join('{0}x'.format(factor), name)
        return name

    def generate(self, factor=1):
        thumb_name = self.get_storage_name(factor)

        tmpfile = MoveableNamedTemporaryFile(thumb_name)
        resizer = GmConvertCommand(
            infile=self.source,
            outfile=tmpfile.temporary_file_path(),
            options=self.get_gm_options(factor)
        )
        assert resizer.execute(fail_silently=True)

        if self.options['pngquant'] and os.path.splitext(thumb_name)[1] == '.png':
            optimizer = PngquantCommand(
                pngfile=tmpfile.temporary_file_path(), quality=self.options['pngquant'])
            assert optimizer.execute()

        thumbnail_storage.save(thumb_name, tmpfile)

        return True

    def get_gm_options(self, factor=1):
        gm_options = OrderedDict()

        # Remove any icc profiles to avoid problems.
        gm_options['+profile'] = '"*"'

        size = self.get_estimated_size()

        resize_attrs = ''
        if self.options['upscale']:
            if self.options['crop']:
                resize_attrs = '^'
        else:
            if self.options['crop']:
                resize_attrs = '^'
            else:
                resize_attrs = '>'

        gm_options['resize'] = '{0}x{1}{2}'.format(
            factor_size(size[0], factor),
            factor_size(size[1], factor),
            resize_attrs
        )

        if self.options['crop']:
            gm_options['gravity'] = 'Center'
            gm_options['crop'] = '{0}x{1}+0+0'.format(
                factor_size(size[0], factor),
                factor_size(size[1], factor)
            )

        gm_options['quality'] = self.options['quality']

        return gm_options
