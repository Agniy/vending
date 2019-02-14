from django.db import models
from django.db.models import Sum
from vending.default_manager import DefaultManager



class Coin(models.Model):
    title = models.CharField('Валюта', max_length=255)
    code = models.CharField('Код', max_length=255,db_index=True)
    value = models.PositiveSmallIntegerField('Номинал')
    objects = DefaultManager()

    class Meta:
        verbose_name = "монеты"
        verbose_name_plural = "монеты"

class AbstractCashManager(DefaultManager):
    def get_all_dict(self):
        return dict(((c.id,{
            "id":c.id,
            "value":c.coin.value,
            "count":c.cnt
        }) for c in self.select_related('coin').all().order_by('coin__value')))

    def get_summ(self):
        summ = 0
        for cash in self.select_related('coin').filter(cnt__gt=0):
            summ += cash.cnt * cash.coin.value
        return summ

class AbstractCash(models.Model):
    coin = models.ForeignKey(Coin,verbose_name="Монета",on_delete=models.CASCADE)
    cnt = models.PositiveIntegerField('Количество',default=0)
    objects = AbstractCashManager()
    class Meta:
        verbose_name ="деньга"
        verbose_name_plural = "деньги"
        abstract = True

class UserCash(AbstractCash):
    class Meta:
        verbose_name ="деньги покупателя"
        verbose_name_plural = "деньги покупателя"

class VMCash(AbstractCash):
    class Meta:
        verbose_name ="деньги машины"
        verbose_name_plural = "деньги машины"

class UserVMCash(AbstractCash):
    class Meta:
        verbose_name ="активные деньги"
        verbose_name_plural = "активные деньги"

class Product(models.Model):
    title = models.CharField('Название', max_length=255)
    cnt = models.PositiveIntegerField('Остаток',default=0)
    price = models.PositiveIntegerField('Сумма',default=0)
    sort = models.PositiveSmallIntegerField('Количество',default=0)
    objects = DefaultManager()

    class Meta:
        verbose_name ="товар"
        verbose_name_plural = "товар"

class Order(models.Model):
    product = models.ForeignKey(Product,verbose_name="Товар",on_delete=models.CASCADE)
    count = models.PositiveSmallIntegerField('Количество')
    summ = models.PositiveIntegerField('Сумма')
    cdate = models.DateTimeField('Создан', auto_now_add=True)
    objects = DefaultManager()

    class Meta:
        verbose_name ="заказ"
        verbose_name_plural = "заказы"