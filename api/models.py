from django.db import models


class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(default='description')
    price = models.IntegerField(default=0)
    currency = models.CharField(default='usd', max_length=10)


class Order(models.Model):
    order_num = models.IntegerField(default=0)
    product_num = models.ForeignKey(Item, on_delete=models.DO_NOTHING)
    quantity = models.IntegerField(default=1)
