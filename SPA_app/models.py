from django.db import models


class Medicines(models.Model):
    name = models.CharField(max_length=255)
    photo = models.URLField(max_length=255)
    price = models.IntegerField()
    url = models.URLField(max_length=255)
    pharmacy = models.CharField(max_length=255)

    class Meta:
        db_table = "medicines"


class Products(models.Model):
    name = models.CharField(max_length=255)
    photo = models.URLField(max_length=255)

    class Meta:
        db_table = "products"


class Pharmacies(models.Model):
    price = models.IntegerField()
    url = models.URLField(max_length=255)
    pharmacy = models.CharField(max_length=255)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)

    class Meta:
        db_table = "pharmacies"
