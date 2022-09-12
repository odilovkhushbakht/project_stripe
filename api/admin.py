from django.contrib import admin

from api.models import Item, Order


@admin.register(Item)
class AdminItem(admin.ModelAdmin):
    list_display = ['id', 'name', 'price', 'currency']


@admin.register(Order)
class AdminOrder(admin.ModelAdmin):
    list_display = ['id', 'order_num', 'product_num', 'quantity']
