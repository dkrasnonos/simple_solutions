from django.db import models


class Item(models.Model):
    name = models.CharField(max_length=50, verbose_name='Наименование')
    description = models.CharField(max_length=200, blank=True, verbose_name='Описание')
    price = models.FloatField(verbose_name='Цена, руб.')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
