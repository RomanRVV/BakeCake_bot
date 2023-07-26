from django.db import models


class CakeBase(models.Model):
    base_of_cake = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.base_of_cake}'


class Level(models.Model):
    num_of_level = models.IntegerField(max_value=3, min_value=1)
    shape = models.ForeignKey(CakeBase)

    def __str__(self):
        return f'{self.num_of_level} уровневый {self.shape} формы'


class CakeTopping(models.Model):
    topping_for_cake = models.CharField(max_length=100, null=True)


class Cake(models.Model):
    prise = models.FloatField(max_digits=6, decimal_places=2)
    level = models.ForeignKey(
        Level,
        on_delete=models.CASCADE)
    cream = models.CharField(max_length=100)
    topping = models.ForeignKey(CakeTopping, on_delete=models.CASCADE)

    def __srt__(self):
        return f'Торт{self.level} c {self.cream} и {self.topping} стоимостью {self.prise}'
