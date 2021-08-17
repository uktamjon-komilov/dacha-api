from django.db import models


class Dacha(models.Model):
    image = models.ImageField(upload_to="images/")
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.FloatField()
    phone = models.CharField(max_length=16)