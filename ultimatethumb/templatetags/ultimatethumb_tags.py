import os

from django.template import Library

from ..thumbnail import ThumbnailSet
from ..utils import parse_source

VALID_IMAGE_FILE_EXTENSIONS = ('jpg', 'jpeg', 'png', 'gif', 'ico')

register = Library()


@register.simple_tag(takes_context=True)
def ultimatethumb(
    context,
    as_var,
    source,
    sizes=None,
    upscale=False,
    crop=None,
    retina=True,
    quality=None,
    pngquant=None,
):
    """
    Main template tag to generate thumbnail sourcesets.
    """
    source = parse_source(source)

    if not source:
        context[as_var] = None
        return ''

    source_extension = os.path.splitext(source)[1].lower().lstrip('.')
    if source_extension not in VALID_IMAGE_FILE_EXTENSIONS:
        context[as_var] = None
        return ''

    thumbnail_options = {'upscale': upscale, 'factor2x': retina}

    if crop is not None:
        thumbnail_options['crop'] = crop

    if quality is not None:
        thumbnail_options['quality'] = quality

    if pngquant is not None:
        thumbnail_options['pngquant'] = pngquant

    context[as_var] = ThumbnailSet(source, sizes, thumbnail_options).thumbnails
    return ''
