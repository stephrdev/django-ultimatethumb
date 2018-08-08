import factory

from tests.resources.mockapp.models import ImageModel


class ImageModelFactory(factory.DjangoModelFactory):
    file = factory.django.ImageField(
        filename='image.jpg', color='orange', width=50, height=100)

    class Meta:
        model = ImageModel
