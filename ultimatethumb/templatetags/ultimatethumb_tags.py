import os

from django.conf import settings
from django.contrib.staticfiles.finders import find
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.files.storage import default_storage
from django.template import Library

from ..thumbnail import Thumbnail
from ..utils import get_size_for_path, parse_sizes


VALID_IMAGE_FILE_EXTENSIONS = ('jpg', 'jpeg', 'png', 'gif', 'ico')

register = Library()


@register.simple_tag(takes_context=True)
def ultimatethumb(
    context,
    as_var,
    source,
    sizes=None,
    upscale=False,
    crop=False,
    retina=True,
    quality=90
):
    if source.startswith('static:'):
        source = find(source[7:])

        # Don't hash if in debug mode. This will also fail hard if the
        # staticfiles storage doesn't support hashing of filenames.
        if not settings.DEBUG:
            source = staticfiles_storage.hashed_name(source)
    else:
        if not source.startswith('/'):
            source = default_storage.path(source)

    if not source:
        context[as_var] = None
        return ''

    source_extension = os.path.splitext(source)[1].lower().lstrip('.')
    if source_extension not in VALID_IMAGE_FILE_EXTENSIONS:
        context[as_var] = None
        return ''

    thumbnails = []

    source_size = get_size_for_path(source)

    # If retina option is enabled, pretend that the source is half as large as
    # it is. We do this to ensure that we have "retina" images which effectively
    # are doubled in size. Doing this, we never have to upscale the image.
    if retina:
        source_size = (int(source_size[0] / 2), int(source_size[1] / 2))

    oversize = False

    for size in parse_sizes(sizes):
        if '%' not in size[0] and not upscale:
            if int(size[0]) > source_size[0] or int(size[1]) > source_size[1]:
                size = [str(source_size[0]), str(source_size[1])]
                oversize = True

        thumbnails.append(
            Thumbnail(source, {
                'size': size,
                'upscale': upscale,
                'crop': crop,
                'quality': quality
            }))

        if oversize:
            break

    context[as_var] = thumbnails
    return ''
