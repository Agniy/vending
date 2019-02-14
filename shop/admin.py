from django.contrib import admin
from shop.models import Coin

class CoinAdmin(admin.ModelAdmin):
    list_display = ('title','code','value')

admin.site.register(Coin, CoinAdmin)