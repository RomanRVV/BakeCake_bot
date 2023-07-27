
from django.db import models



class Cake(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='cakes/')


class CakeConstructor(models.Model):
    CAKE_BASE_CHOICES = [
        ('vanila', 'Ванильный бисквит'),
        ('choco', 'Шоколадный бисквит'),
        ('marble', 'Мраморный бисквит')
    ]
    TOPPING_CHOICES = [
        ('wedge', 'Клиновый сироп'),
        ('caramel', 'Карамельный сироп')
    ]
    LEVEL_CHOICES = [
        ('one', '1 уровень'),
        ('two', '2 уровня'),
        ('three', '3 уровня')
    ]
    num_of_level = models.CharField(max_length=5, choices=LEVEL_CHOICES,
                                    verbose_name='Количество уровней торта',
                                    default='one')
    base_of_cake = models.CharField(max_length=6,
                                    choices=CAKE_BASE_CHOICES,
                                    default='vanila',
                                    verbose_name='Основа для торта')
    topping = models.CharField(max_length=7,
                               choices=TOPPING_CHOICES,
                               blank=True,
                               verbose_name='Топпинг')
    blackberry = models.BooleanField(verbose_name='Еживика', default=False)
    raspberry = models.BooleanField(verbose_name='Малина', default=False)
    blueberry = models.BooleanField(verbose_name='Голубика', default=False)


class LinkStatistics(models.Model):
    title = models.CharField(max_length=200, verbose_name='Bitly ссылка')
    description = models.TextField(verbose_name='Описание ссылки')
    transitions = models.IntegerField(verbose_name='Количество переходов по ссылке', default=0)