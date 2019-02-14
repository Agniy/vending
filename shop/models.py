from django.db import models
from vending.default_manager import DefaultManager

class Coin(models.Model):
    title = models.CharField('Валюта', max_length=255)
    code = models.CharField('Код', max_length=255,db_index=True)
    value = models.PositiveSmallIntegerField('Номинал')
    objects = DefaultManager()

    class Meta:
        verbose_name = "монеты"
        verbose_name_plural = "монеты"

class AbstractCash(models.Model):
    coin = models.ForeignKey(Coin,verbose_name="Монета",on_delete=models.CASCADE)
    count = models.PositiveIntegerField('Количество',default=0)
    objects = DefaultManager()

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
    count = models.PositiveIntegerField('Остаток',default=0)
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