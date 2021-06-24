from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.CharField(max_length=200)
    url = models.CharField(max_length=200)
    img = models.CharField(max_length=200)
