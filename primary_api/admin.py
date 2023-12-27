from django.contrib import admin
from primary_api.models import Item, Order, Tax, Discount, OrderItem

admin.site.register(Item)
admin.site.register(Order)
admin.site.register(Tax)
admin.site.register(Discount)
admin.site.register(OrderItem)