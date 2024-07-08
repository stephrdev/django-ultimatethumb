import os
from urllib.parse import urlparse

from django.conf import settings
from django.http import Http404, HttpResponse, HttpResponseNotModified
from django.utils.http import http_date
from django.views.generic import View
from django.views.static import was_modified_since

from .thumbnail import Thumbnail


class ThumbnailView(View):
    """
    ThumbnailView is used to provide the thumbnails to the brower.

    We don't use a serve static view because we need to check if the requested
    thumbnail is available - and if not: generate one.

    The view supports the X-Accel-Redirect header supported by Nginx to no really
    serve the binary (enabled by default if DEBUG is False).
    """

    def get(self, *args, **kwargs):
        """
        Fetch and return the thumbnail response.
        """
        return self.render_thumbnail(self.get_thumbnail(), self.get_factor())

    def get_thumbnail(self):
        """
        Try to fetch the thumbnail based on the thumbnail name.
        Might fail if cache resets between generation of the thumbnail urls and
        fetching of the images.
        """
        try:
            return Thumbnail.from_name(self.kwargs['name'])
        except KeyError:
            raise Http404

    def get_factor(self):
        """
        Get factor from url.
        """
        return int(self.kwargs.get('factor', '1'))

    def render_thumbnail(self, thumbnail, factor):
        """
        Generate the http response for the requested thumbnail.
        The code is able response with 304 if the thumbnail was already requested.

        Supports X-Accel-Redirect, enabled by default if DEBUG is False.
        """
        path = thumbnail.get_storage_path(factor)

        thumbnail_stat = os.stat(path)
        mimetype = thumbnail.get_mimetype()

        # Check for last modified.
        if not was_modified_since(
            self.request.META.get('HTTP_IF_MODIFIED_SINCE'),
            thumbnail_stat.st_mtime,
        ):
            return HttpResponseNotModified()

        if getattr(settings, 'ULTIMATETHUMB_USE_X_ACCEL_REDIRECT', not settings.DEBUG):
            response = HttpResponse(content_type=mimetype)
            response['X-Accel-Redirect'] = urlparse(thumbnail.get_storage_url(factor)).path
        else:
            with open(path, 'rb') as file:
                response = HttpResponse(file.read(), content_type=mimetype)

        # Respect the If-Modified-Since header.
        response['Last-Modified'] = http_date(thumbnail_stat.st_mtime)
        response['Content-Length'] = thumbnail_stat.st_size

        return response
