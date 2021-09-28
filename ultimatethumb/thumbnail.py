import base64
import os
from collections import OrderedDict, namedtuple
from mimetypes import guess_type

from django.conf import settings
from django.utils.functional import cached_property

from .commands import GraphicsmagickCommand, PngquantCommand
from .storage import thumbnail_storage
from .utils import (
    MoveableNamedTemporaryFile,
    build_url,
    factor_size,
    get_size_for_path,
    get_thumb_data,
    get_thumb_name,
    parse_sizes,
)

CROP_GRAVITY = {
    True: 'Center',
    1: 'Center',
    'C': 'Center',
    'N': 'North',
    'NW': 'NorthWest',
    'NE': 'NorthEast',
    'W': 'West',
    'E': 'East',
    'S': 'South',
    'SW': 'SouthWest',
    'SE': 'SouthEast',
    'Center': 'Center',
    'North': 'North',
    'NorthWest': 'NorthWest',
    'NorthEast': 'NorthEast',
    'West': 'West',
    'East': 'East',
    'South': 'South',
    'SouthWest': 'SouthWest',
    'SouthEast': 'SouthEast',
}


Size = namedtuple('Size', ('width', 'height'))


class ThumbnailSet(object):
    """
    A ThumbnailSet holds the source configuration and a number of thumbnails as requested.
    """

    def __init__(self, source, sizes, options):
        """
        Takes a valid source and a list of requested sizes together with additional options.
        """
        self.source = source
        self.sizes = sizes
        self.options = options

    @cached_property
    def thumbnails(self):
        """
        The thumbnails property returns a list of available thumbnails.
        """
        return self.get_thumbnails()

    def get_source_size(self):
        """
        Returns the file size of the source.

        If retina option is enabled, pretend that the source is half as large as
        it is. We do this to ensure that we have "retina" images which effectively
        are doubled in size. Doing this, we never have to upscale the image.
        """
        source_size = get_size_for_path(self.source)
        if self.options.get('factor2x', True):
            source_size = int(source_size[0] / 2), int(source_size[1] / 2)

        return source_size

    def get_sizes(self):
        """
        Parse the given sizes and return a list of size requests.
        """
        return parse_sizes(self.sizes)

    def get_thumbnails(self):
        """
        Returns a list of thumbnails based on the requested sizes.
        Some additional calculations are done to make sure we don't return thumbnails
        larger than the source file is.
        """
        thumbnails = []
        source_size = self.get_source_size()

        oversize = False
        for size in self.get_sizes():
            if '%' not in size[0] and not self.options.get('upscale', False):
                thumb_size = (int(size[0]), int(size[1]))
                if thumb_size[0] >= source_size[0] or thumb_size[1] >= source_size[1]:
                    if self.options.get('crop', False):
                        size[0] = str(min(source_size[0], thumb_size[0]))
                        size[1] = str(min(source_size[1], thumb_size[1]))
                    else:
                        if thumb_size[0] >= source_size[0]:
                            factor = float(source_size[0]) / thumb_size[0]
                            size[0] = str(source_size[0])
                            size[1] = (
                                str(int(round(thumb_size[1] * factor)))
                                if thumb_size[1]
                                else '0'
                            )
                        else:
                            factor = float(source_size[1]) / thumb_size[1]
                            size[0] = (
                                str(int(round(thumb_size[0] * factor)))
                                if thumb_size[0]
                                else '0'
                            )
                            size[1] = str(source_size[1])

                    oversize = True

            options = {'size': size[0:2]}
            if len(size) == 4:
                options['viewport'] = size[2:4]

            options.update(self.options)
            thumbnails.append(Thumbnail(self.source, options))

            if oversize:
                break

        return thumbnails


class Thumbnail(object):
    """
    This object represents a single thumbnail.
    """

    def __init__(self, source, opts):
        """
        Given a source and options, this method initializes the Thumbnail object.
        Some validation on the provided options are done.
        """
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
            ' '.join(['{0}={1}'.format(k, self.options[k]) for k in sorted(self.options)]),
        )

    @classmethod
    def from_name(cls, name):
        """
        Using a name, reconstruct a thumbnail object.
        The name is actually a cache key which is used by get_thumb_data to fetch the
        original thumbnail configuration.
        """
        return Thumbnail(*get_thumb_data(name))

    def get_name(self):
        """
        Generate the thumbnail name for the current thumbnail configuration.
        """
        return get_thumb_name(
            self.source,
            **dict(
                (option, value)
                for option, value in self.options.items()
                if option not in ('viewport',)
            )
        )

    @cached_property
    def size(self):
        """
        The size property returns the calculated, estimated thumbnail size without
        actually generating the thumbnail image.
        """
        return self.get_estimated_size()

    @cached_property
    def viewport(self):
        """
        Returns the valid viewport for this thumbnail, might be used in templates to
        configure the source sets properly.
        """
        viewport = self.options.get('viewport', None)

        if not viewport:
            return self.size

        return Size(
            int(viewport[0]) if viewport[0] != '0' else None,
            int(viewport[1]) if viewport[1] != '0' else None,
        )

    @property
    def url(self):
        """
        The url property is responsible for returning the acutal thumbnail url.
        """
        return build_url(self.get_name())

    @property
    def url_2x(self):
        """
        Returns the retina url for the thumbnail if retina is enabled.
        """
        return build_url(self.get_name(), 2) if self.options['factor2x'] else None

    @property
    def base64(self):
        """
        Returns the base64 representation of the thumbnail to use in a src attribute.
        """
        return 'data:{0};base64,{1}'.format(self.get_mimetype(), self.get_base64_content())

    @property
    def requested_size(self):
        """
        Returns the requested thumbnail size.
        """
        return Size(*self.options['size'])

    def exists(self, factor=1):
        """
        Checks if the thumbnail already exists.
        """
        return os.path.exists(self.get_storage_path(factor, generate=False))

    def get_mimetype(self):
        """
        Returns the mime type of the thumbnail based on the thumbnail file name.
        """
        mimetype, encoding = guess_type(self.get_name())
        return mimetype or 'application/octet-stream'

    def get_storage_url(self, factor=1):
        """
        Returns the real url to use in the ultimatethumb view for returning the image.
        """
        return thumbnail_storage.url(self.get_storage_name(factor))

    def get_storage_path(self, factor=1, generate=True):
        """
        Returns the storage path in filesystem of the thumbnail file.
        """
        if generate and not self.exists(factor):
            self.generate(factor)

        return thumbnail_storage.path(self.get_storage_name(factor))

    def get_size(self, factor=1):
        """
        Returns the actual generated thumbnail image size.
        """
        return Size(*get_size_for_path(self.get_storage_path(factor)))

    def get_estimated_size(self):
        """
        Calculates the estimated thumbnail image dimensions based on the source size
        and the options provided.
        """
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

    def get_storage_name(self, factor=1, suffix=None):
        """
        Returns the name to use when storing the thumbnail to disk.
        """
        name = self.get_name()
        if factor != 1:
            name = os.path.join('{0}x'.format(factor), name)
        if suffix:
            name = '{0}.{1}'.format(os.path.splitext(name)[0], suffix)
        return name

    def generate(self, factor=1):
        """
        Genrate the thumbnail using Graphicsmagick and Pngquant (if enabled and
        source image is a png file.
        """
        thumb_name = self.get_storage_name(factor)

        tmpfile = MoveableNamedTemporaryFile(thumb_name)
        resizer = GraphicsmagickCommand(
            infile=self.source,
            outfile=tmpfile.temporary_file_path(),
            options=self.get_gm_options(factor),
        )
        assert resizer.execute(fail_silently=True)

        if self.options['pngquant'] and os.path.splitext(thumb_name)[1] == '.png':
            optimizer = PngquantCommand(
                pngfile=tmpfile.temporary_file_path(), quality=self.options['pngquant']
            )
            assert optimizer.execute()

        thumbnail_storage.save(thumb_name, tmpfile)

        return True

    def get_gm_options(self, factor=1):
        """
        Generates the option set dor Graphicsmagick to generate the thumbnail.
        """
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
            factor_size(size[0], factor), factor_size(size[1], factor), resize_attrs
        )

        crop = CROP_GRAVITY.get(self.options['crop'], False)
        if crop:
            gm_options['gravity'] = crop
            gm_options['crop'] = '{0}x{1}+0+0'.format(
                factor_size(size[0], factor), factor_size(size[1], factor)
            )

        gm_options['quality'] = self.options['quality']

        return gm_options

    def get_base64_content(self):
        """
        Reads the base64 version of the thumbnail from disk and returns content.
        """
        with open(self.get_base64_path(), 'r') as b64image:
            return b64image.read()

    def get_base64_path(self, generate=True):
        """
        Calculates the path of the base64 image version.
        If path does not exist, base64 version is generated.
        """
        path = thumbnail_storage.path(self.get_storage_name(suffix='base64'))
        if generate and not os.path.exists(path):
            self.generate_base64()

        return path

    def generate_base64(self):
        """
        Generate the base64 representation from the generated thumbnail image file.
        """
        thumb_name = self.get_storage_name(suffix='base64')

        tmpfile = MoveableNamedTemporaryFile(thumb_name)

        with open(self.get_storage_path(), 'rb') as thumb_image:
            tmpfile.file.write(base64.b64encode(thumb_image.read()))
            tmpfile.file.flush()

        thumbnail_storage.save(thumb_name, tmpfile)
        return True
