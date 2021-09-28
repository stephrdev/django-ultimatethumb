import hashlib
import json
import os
import re
import stat
import tempfile
from collections import OrderedDict
from urllib.parse import urljoin, urlparse

from django.conf import settings
from django.contrib.staticfiles.finders import find
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.cache import cache
from django.core.files.storage import default_storage
from django.urls import reverse
from django.utils.encoding import force_bytes
from PIL import Image as PILImage

SIZE_RE = re.compile(r'^(\d+%?)(?:x(\d+%?))?(?:\:(\d+)(?:x(\d+))?)?$')


def get_cache_key(key):
    """
    Generates a prefixed cache-key for ultimatethumb.
    """
    return 'ultimatethumb:{0}'.format(key)


def get_thumb_name(source, **options):
    """
    Builds the thumbnail name and uses the name to store the source and options
    to cache.
    """
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
    """
    Uses the thumbail name and fetches the source and options from cache.
    """
    cache_key = get_cache_key(thumb_name)
    serialized_data = cache.get(cache_key)
    if not serialized_data:
        raise KeyError('Invalid thumb_name')

    data = json.loads(serialized_data)
    return (data['source'], data['opts'])


def parse_source(source):
    """
    Parse and lookup the file system path for a given source.
    The function understands both media names and static names
    (if prefixed with "static:")
    """
    if source.startswith('static:'):
        source = source[7:]

        # Don't hash if in debug mode. This will also fail hard if the
        # staticfiles storage doesn't support hashing of filenames.
        if not settings.DEBUG:
            # We always should have used stored_name because hashed_name
            # calculates the name on the fly. For backwards compatibility we
            # try to use stored_name but fall back to hashed_name.
            if hasattr(staticfiles_storage, 'stored_name'):
                source = staticfiles_storage.stored_name(source)
            else:
                source = staticfiles_storage.hashed_name(source)
            source = staticfiles_storage.path(source)
        else:
            source = find(source)
    else:
        if not source.startswith('/'):
            source = default_storage.path(source)

    return source


def parse_sizes(value):
    """
    Parses and returns a list of thumbnail sizes.
    """
    sizes = value.split(',')

    parsed_sizes = []
    for size in sizes:
        parsed_size = SIZE_RE.match(size)
        if not parsed_size:
            raise ValueError('{0} is not a valid size'.format(size))

        parts = parsed_size.groups()
        size = [parts[0], parts[1] or '0']
        if parts[2]:
            size += [parts[2], parts[3] or '0']

        parsed_sizes.append(size)

    return parsed_sizes


def factor_size(value, factor):
    """
    Factors the given thumbnail size. Understands both absolute dimensions
    and percentages.
    """
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
    """
    Returns the given url prefixed with a domain if configured in settings.
    """
    domain = getattr(settings, 'ULTIMATETHUMB_DOMAIN', '')

    if domain:
        parsed_domain = urlparse(domain)
        # If the domain has no scheme, prepend slashes to make sure the url is
        # correctly joined.
        if not parsed_domain.netloc and parsed_domain.path:
            domain = '//{0}'.format(domain)

    return urljoin(domain, url)


def build_url(name, factor=1):
    """
    Build the actual url for a given name and factor.
    """
    if factor > 1:
        url = reverse('thumbnail-factor', kwargs={'factor': factor, 'name': name})
    else:
        url = reverse('thumbnail', kwargs={'name': name})

    return get_domain_url(url)


class MoveableNamedTemporaryFile(object):
    def __init__(self, name):
        suffix = os.path.splitext(os.path.basename(name))[1]
        self.file = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)

        perms = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH

        os.chmod(self.file.name, perms)
        self.name = name

    def chunks(self):
        return self.file.read()

    def close(self):
        return self.file.close()

    def temporary_file_path(self):
        return self.file.name
