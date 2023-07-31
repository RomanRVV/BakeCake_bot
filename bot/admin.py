from django.contrib import admin
from .models import *


@admin.register(Cake)
class CakeAdmin(admin.ModelAdmin):
     list_display = ('name', 'price')



@admin.register(CakeConstructor)
class CakeConstructorAdmin(admin.ModelAdmin):
    list_display = ('num_of_level',
                    'cake_shape',
                    'base_of_cake',
                    'topping',
                    'berries',
                    'price')


@admin.register(CakeOrder)
class CakeOrderAdmin(admin.ModelAdmin):
    list_display = ('user_name',
                    'user_phone',
                    'cake',
                    'designer_cake',
                    'order_price')


@admin.register(LinkStatistics)
class LinkStatisticsAdmin(admin.ModelAdmin):
    readonly_fields = ('transitions',
                       'bitlink')
    list_display = ('description',
                    'bitlink',
                    'transitions')
