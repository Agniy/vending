from django.db import models

class Coin(models.Model):
    img = models.ImageField(upload_to='coins', verbose_name='Изображение',max_length=255)
    value = models.PositiveSmallIntegerField('Номинал')

    class Meta:
        verbose_name = "монеты"
        verbose_name_plural = "монеты"

class AbstractCash(models.Model):
    coin = models.ForeignKey(Coin,verbose_name="Монета",on_delete=models.CASCADE)
    count = models.PositiveIntegerField('Количество')

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

class Product(models.Model):
    title = models.CharField('Название', max_length=255)
    price = models.PositiveIntegerField('Количество')
    sort = models.PositiveSmallIntegerField('Номинал')

    class Meta:
        verbose_name ="товар"
        verbose_name_plural = "товар"

class Order(models.Model):
    product = models.ForeignKey(Product,verbose_name="Товар",on_delete=models.CASCADE)
    count = models.PositiveSmallIntegerField('Количество')
    summ = models.PositiveIntegerField('Сумма')
    cdate = models.DateTimeField('Создан', auto_now_add=True)

    class Meta:
        verbose_name ="заказ"
        verbose_name_plural = "заказы"