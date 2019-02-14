from django.core.management.base import BaseCommand
from shop.models import Coin,Product,UserCash,VMCash

def fill_all_data():
    coins = {c.value:c for c in Coin.objects.filter(code="rub")}

    #fill UserCash
    # ------------------------------------------------
    c,created = UserCash.objects.get_or_create(coin=coins[1])
    c.count = 10
    c.save()
    c,created = UserCash.objects.get_or_create(coin=coins[2])
    c.count = 30
    c.save()
    c,created = UserCash.objects.get_or_create(coin=coins[5])
    c.count = 20
    c.save()
    c,created = UserCash.objects.get_or_create(coin=coins[10])
    c.count = 15
    c.save()
    # ------------------------------------------------

    #fill VMCash
    # ------------------------------------------------
    c,created = VMCash.objects.get_or_create(coin=coins[1])
    c.count = 100
    c.save()
    c,created = VMCash.objects.get_or_create(coin=coins[2])
    c.count = 100
    c.save()
    c,created = VMCash.objects.get_or_create(coin=coins[5])
    c.count = 100
    c.save()
    c,created = VMCash.objects.get_or_create(coin=coins[10])
    c.count = 100
    c.save()
    # ------------------------------------------------

    #fill Product
    # ------------------------------------------------
    p,created = Product.objects.get_or_create(title="Чай")
    p.price = 13
    p.count = 10
    p.sort = 0;
    p.save()
    p, created = Product.objects.get_or_create(title="Кофе")
    p.price = 18
    p.count = 20
    p.sort = 1;
    p.save()
    p, created = Product.objects.get_or_create(title="Кофе с молоком")
    p.price = 21
    p.count = 20
    p.sort = 2;
    p.save()
    p, created = Product.objects.get_or_create(title="Сок")
    p.price = 35
    p.count = 15
    p.sort = 3;
    p.save()
    # ------------------------------------------------


class Command(BaseCommand):
    def handle(self, *args, **options):
        fill_all_data()

'''
Example usage:
    python manage.py fill_data
'''