import pytest
from django.core.urlresolvers import reverse

from ultimatethumb.tests.factories.mockapp import ImageModelFactory
from ultimatethumb.thumbnail import Thumbnail


@pytest.mark.django_db
class TestThumbnailView:
    def setup(self):
        self.image = ImageModelFactory.create()
        self.thumbnail = Thumbnail(self.image.file.path, {'size': [50, 50]})

    def test_get(self, client, settings):
        settings.ULTIMATETHUMB_USE_X_ACCEL_REDIRECT = False
        response = client.get(self.thumbnail.url)

        assert response.status_code == 200
        assert 'Last-Modified' in response
        assert 'Content-Length' in response
        assert 'Content-Disposition' not in response
        assert 'x-accel-redirect' not in response._headers

    def test_get_invalid(self, client):
        response = client.get(reverse('thumbnail', kwargs={
            'name': 'testtesttesttesttesttesttesttesttesttest/foobar.jpg'
        }))
        assert response.status_code == 404

    def test_get_x_accel_redirect(self, client, settings):
        settings.ULTIMATETHUMB_USE_X_ACCEL_REDIRECT = True
        response = client.get(self.thumbnail.url)

        assert response.status_code == 200
        assert response['X-Accel-Redirect'] == self.thumbnail.get_storage_url()

    def test_get_last_modified(self, client, settings):
        settings.ULTIMATETHUMB_USE_X_ACCEL_REDIRECT = True
        response = client.get(self.thumbnail.url)

        assert response.status_code == 200

        response2 = client.get(
            self.thumbnail.url,
            HTTP_IF_MODIFIED_SINCE=response['Last-Modified']
        )
        assert response2.status_code == 304
