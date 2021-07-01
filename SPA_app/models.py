from django.db import models


class Medicine(models.Model):
    title = models.CharField(max_length=255, verbose_name="title")
    photo = models.URLField(max_length=255, null=True, verbose_name="photo")
    price = models.FloatField(verbose_name="price")
    url = models.URLField(max_length=255, verbose_name="url")
    pharmacy = models.CharField(max_length=255, verbose_name="pharmacy")

    class Meta:
        verbose_name = "medicine"
        db_table = "medicine"


class Product(models.Model):
    title = models.CharField(max_length=255, verbose_name="title")
    photo = models.URLField(max_length=255, null=True, verbose_name="photo")

    class Meta:
        verbose_name = "product"
        db_table = "product"


class Pharmacy(models.Model):
    price = models.FloatField(verbose_name="price")
    url = models.URLField(max_length=255, verbose_name="url")
    pharmacy = models.CharField(max_length=255, verbose_name="pharmacy")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="product")

    class Meta:
        verbose_name = "pharmacy"
        db_table = "pharmacy"
