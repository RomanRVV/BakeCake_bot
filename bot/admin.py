from django.contrib import admin
from .models import *


@admin.register(Cake)
class CakeAdmin(admin.ModelAdmin):
    list_display = ('name',
                       'price')


@admin.register(CakeConstructor)
class CakeConstructorAdmin(admin.ModelAdmin):
    pass


@admin.register(CakeOrder)
class CakeOrderAdmin(admin.ModelAdmin):
    list_display = ('user_name',
                    'user_phone',
                    'cake',
                    'designer_cake',)


@admin.register(LinkStatistics)
class LinkStatisticsAdmin(admin.ModelAdmin):
    readonly_fields = ('transitions',
                       'bitlink')
    list_display = ('description',
                    'bitlink',
                    'transitions')


