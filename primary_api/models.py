from django.db import models


class Item(models.Model):
    name = models.CharField(max_length=50, verbose_name='Наименование')
    description = models.CharField(max_length=200, blank=True, verbose_name='Описание')
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Цена')
    currency = models.CharField(max_length=3, choices=[('USD', 'Доллар США'), ('RUB', 'Рубль')], default='RUB',
                                verbose_name='Валюта')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"


class Discount(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='discounts')
    name = models.CharField(max_length=50, verbose_name='Наименование скидки')
    amount = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Сумма скидки')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Скидка"
        verbose_name_plural = "Скидки"


class Tax(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='taxes')
    name = models.CharField(max_length=50, verbose_name='Наименование налога')
    percentage = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Процент налога')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Налог"
        verbose_name_plural = "Налоги"


class Order(models.Model):
    items = models.ManyToManyField(Item, through='OrderItem', verbose_name='Товары')

    def get_total_price(self):
        total_price = 0
        price_of_items = 0
        order_items = OrderItem.objects.filter(order=self)
        for order_item in order_items:
            price_of_items += order_item.item.price * order_item.quantity
        initial_price = price_of_items
        discount = sum(discount.amount for discount in self.discounts.all())
        taxes = self.taxes.all()
        for tax in taxes:
            total_price += (price_of_items * tax / 100)
        total_price = total_price + initial_price - discount
        return total_price

    def __str__(self):
        return f'Заказ №{self.id}'

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='Заказ')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, null=True, verbose_name='Товар')
    quantity = models.PositiveIntegerField(verbose_name='Количество')

    def __str__(self):
        return f"{self.quantity} x {self.item.name} в заказе {self.order.id}"
    class Meta:
        verbose_name = "Товар в заказе"
        verbose_name_plural = "Товары в заказах"
