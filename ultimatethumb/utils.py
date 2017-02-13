import hashlib
import json
import os
import re
from collections import OrderedDict

from django.conf import settings
from django.contrib.staticfiles.finders import find
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.cache import cache
from django.core.files.storage import default_storage
from django.core.urlresolvers import reverse
from django.utils.encoding import force_bytes
from django.utils.six.moves.urllib import parse as urlparse
from PIL import Image as PILImage


SIZE_RE = re.compile(r'(?:(\d+%?)x(\d+%?))')


def get_cache_key(key):
    """
    Generates a prefixed cache-key for ultimatethumb.
    """
    return 'ultimatethumb:{0}'.format(key)


def get_thumb_name(source, **options):
    source_name, source_ext = os.path.splitext(os.path.basename(source))
    data = OrderedDict()
    data['source'] = source
    data['opts'] = OrderedDict(sorted(options.items(), key=lambda i: i[0]))

    serialized_data = json.dumps(data)
    hashed_data = hashlib.sha1(force_bytes(serialized_data)).hexdigest()

    thumb_name = '{0}/{1}{2}'.format(hashed_data, source_name, source_ext)

    cache_key = get_cache_key(thumb_name)
    if cache_key not in cache:
        cache.set(cache_key, serialized_data)

    return thumb_name


def get_thumb_data(thumb_name):
    cache_key = get_cache_key(thumb_name)
    serialized_data = cache.get(cache_key)
    if not serialized_data:
        raise KeyError('Invalid thumb_name')

    data = json.loads(serialized_data)
    return (data['source'], data['opts'])


def parse_source(source):
    if source.startswith('static:'):
        source = source[7:]

        # Don't hash if in debug mode. This will also fail hard if the
        # staticfiles storage doesn't support hashing of filenames.
        if not settings.DEBUG:
            source = staticfiles_storage.hashed_name(source)
            source = staticfiles_storage.path(source)
        else:
            source = find(source)
    else:
        if not source.startswith('/'):
            source = default_storage.path(source)

    return source


def parse_sizes(value):
    sizes = value.split(',')

    parsed_sizes = []
    for size in sizes:
        parsed_size = SIZE_RE.match(size)
        if not parsed_size:
            raise ValueError('{0} is not a valid size'.format(size))

        parsed_sizes.append([parsed_size.groups()[0], parsed_size.groups()[1]])

    return parsed_sizes


def factor_size(value, factor):
    if type(value) is int:
        size = value * factor
        return str(size) if size else ''

    if value[-1] == '%':
        value = int(value[:-1])
        return '{0}%'.format(value * factor)

    size = int(value) * factor
    return str(size) if size else ''


def get_size_for_path(path):
    """
    Gets the image size for a given path. If the path does not exist, the call
    will fail loud with e.g. OSError exception.
    """
    with open(path, 'rb') as image_file:
        image = PILImage.open(image_file)
        size = image.size
    return size


def get_domain_url(url):
    domain = getattr(settings, 'ULTIMATETHUMB_DOMAIN', '')

    if domain:
        parsed_domain = urlparse.urlparse(domain)
        # If the domain has no scheme, prepend slashes to make sure the url is
        # correctly joined.
        if not parsed_domain.netloc and parsed_domain.path:
            domain = '//{0}'.format(domain)

    return urlparse.urljoin(domain, url)


def build_url(name, factor=1):
    if factor > 1:
        url = reverse('thumbnail-factor', kwargs={'factor': factor, 'name': name})
    else:
        url = reverse('thumbnail', kwargs={'name': name})

    return get_domain_url(url)
