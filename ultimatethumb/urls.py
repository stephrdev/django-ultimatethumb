from django.urls import re_path

from .views import ThumbnailView

urlpatterns = [
    re_path(
        r'^(?P<name>[\w\-]{40}/[\w\-\_\.]+\.\w{3,4})$',
        ThumbnailView.as_view(),
        name='thumbnail',
    ),
    # Prepared to support other factors, currently only 2x.
    re_path(
        r'^(?P<factor>[2])x/(?P<name>[\w\-]{40}/[\w\-\_\.]+\.\w{3,4})$',
        ThumbnailView.as_view(),
        name='thumbnail-factor',
    ),
]
