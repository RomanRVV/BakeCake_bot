import requests
from BakeCake.settings import bitly_token
from django.db import models
from django.contrib.auth.models import User


class Cake(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.IntegerField()
    image = models.ImageField(upload_to='cakes/')


class CakeConstructor(models.Model):
    CAKE_BASE_CHOICES = [
        ('vanila', 'Ванильный бисквит'),
        ('choco', 'Шоколадный бисквит'),
        ('marble', 'Мраморный бисквит'),
        ('honey_biscuits', 'Медовое печенье')
    ]
    TOPPING_CHOICES = [
        ('wedge', 'Кленовый сироп'),
        ('caramel', 'Карамельный сироп'),
        ('milk_choco', 'Молочный шоколад'),
        ('blueberry_syrup', 'Черничный сироп'),
        ('strawberry_syrup', 'Клубничный сироп'),
        ('white_sauce', 'Белый соус')
    ]
    LEVEL_CHOICES = [
        ('one', '1 уровень'),
        ('two', '2 уровня'),
        ('three', '3 уровня')
    ]
    SHAPE_CHOICES = [
        ('square', 'Квадрат'),
        ('circle', 'Круг'),
        ('rectangle', 'Прямоугольник')
    ]
    BERRIES_CHOICES = [
        ('blackberry', 'Еживика'),
        ('raspberry', 'Малина'),
        ('blueberry', 'Голубика'),
        ('strawberry', 'Клубника')
    ]
    name = models.CharField(max_length=200, default='Собранный Вами торт')
    num_of_level = models.CharField(max_length=5, choices=LEVEL_CHOICES,
                                    verbose_name='Количество уровней торта',
                                    default='one')
    cake_shape = models.CharField(max_length=20, choices=SHAPE_CHOICES,
                                  verbose_name='Форма торта',
                                  default='circle')
    base_of_cake = models.CharField(max_length=20,
                                    choices=CAKE_BASE_CHOICES,
                                    default='vanila',
                                    verbose_name='Основа для торта')
    topping = models.CharField(max_length=20,
                               choices=TOPPING_CHOICES,
                               blank=True,
                               verbose_name='Топпинг')
    berries = models.CharField(max_length=20,
                               choices=BERRIES_CHOICES,
                               blank=True,
                               verbose_name='Ягоды')
    inscription = models.CharField(max_length=200,
                                   blank=True,
                                   verbose_name='Надпись на торте')
    price = models.IntegerField(verbose_name='Цена')


class LinkStatistics(models.Model):
    def save(self, *args, **kwargs):
        def shorten_link(token, link):
            url = 'https://api-ssl.bitly.com/v4/bitlinks'
            headers = {
                "Authorization": f"Bearer {token}"
            }
            body = {
                "long_url": link
            }
            response = requests.post(url, headers=headers, json=body)
            response.raise_for_status()
            bitlink = response.json()['link']
            return bitlink

        if self.link:
            self.bitlink = shorten_link(bitly_token, self.link)
        super().save(*args, **kwargs)

    link = models.CharField(max_length=200, verbose_name='Простая ссылка')
    bitlink = models.CharField(max_length=200, verbose_name='Bitly ссылка', blank=True)
    description = models.TextField(verbose_name='Описание ссылки')
    transitions = models.IntegerField(verbose_name='Количество переходов по ссылке', default=0)


class CakeOrder(models.Model):
    user_id = models.CharField(max_length=100, null=True)
    user_name = models.CharField(max_length=100, null=True)
    user_phone = models.CharField(max_length=20, null=True)
    delivery_date = models.DateField(null=True)
    delivery_time = models.TimeField(null=True)
    delivery_address = models.CharField(max_length=200, null=True)
    cake = models.ForeignKey(null=True, on_delete=models.SET_NULL, to='bot.Cake')
    designer_cake = models.ForeignKey(null=True, on_delete=models.CASCADE, to='bot.CakeConstructor')

