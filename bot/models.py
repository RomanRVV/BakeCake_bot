import requests
from BakeCake.settings import bitly_token
from django.db import models


class Member(models.Model):
    chat_id = models.CharField(max_length=100,
                               verbose_name='ID чата участника',
                               null=True, blank=True)
    name = models.CharField(max_length=40, verbose_name='Имя участника',
                            null=True, blank=True)

    def __str__(self):
        return self.name if self.name else "Unnamed member"


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
    client = models.ForeignKey(Member,
                               on_delete=models.CASCADE,
                               verbose_name='Заказчик',
                               related_name='orders')


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