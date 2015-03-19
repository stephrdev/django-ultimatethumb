from django.db import models


class ImageModel(models.Model):
    file = models.ImageField(upload_to='mockapp/imagemodels/')
