import os
from mimetypes import guess_type

from django.conf import settings
from django.http import Http404, HttpResponse, HttpResponseNotModified
from django.utils.http import http_date
from django.views.generic import View
from django.views.static import was_modified_since

from .thumbnail import Thumbnail


class ThumbnailView(View):

    def get(self, *args, **kwargs):
        self.thumbnail = self.get_thumbnail()
        self.factor = self.get_factor()
        return self.render_thumbnail()

    def get_thumbnail(self):
        try:
            return Thumbnail.from_name(self.kwargs['name'])
        except KeyError:
            raise Http404

    def get_factor(self):
        return int(self.kwargs.get('factor', '1'))

    def render_thumbnail(self):
        path = self.thumbnail.get_storage_path(self.factor)

        thumbnail_stat = os.stat(path)
        mimetype, encoding = guess_type(path)

        # No mimetype detected, set default.
        mimetype = mimetype or 'application/octet-stream'

        # Check for last modified.
        if not was_modified_since(
            self.request.META.get('HTTP_IF_MODIFIED_SINCE'),
            thumbnail_stat.st_mtime,
            thumbnail_stat.st_size
        ):
            return HttpResponseNotModified()

        if getattr(settings, 'ULTIMATETHUMB_USE_X_ACCEL_REDIRECT', not settings.DEBUG):
            response = HttpResponse(content_type=mimetype)
            response['X-Accel-Redirect'] = self.thumbnail.get_storage_url(self.factor)
        else:
            with open(path, 'rb') as file:
                response = HttpResponse(file.read(), content_type=mimetype)

        # Respect the If-Modified-Since header.
        response['Last-Modified'] = http_date(thumbnail_stat.st_mtime)
        response['Content-Length'] = thumbnail_stat.st_size

        return response
