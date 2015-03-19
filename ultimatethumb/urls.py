from django.conf.urls import url

from .views import ThumbnailView


urlpatterns = [
    url(
        r'^(?P<name>[\w\-]{40}/[\w\-\_\.]+\.\w{3,4})$',
        ThumbnailView.as_view(),
        name='thumbnail'
    ),

    # Prepared to support other factors, currently only 2x.
    url(
        r'^(?P<factor>[2])x/(?P<name>[\w\-]{40}/[\w\-\_\.]+\.\w{3,4})$',
        ThumbnailView.as_view(),
        name='thumbnail-factor'
    )
]
