from django.db import models
from django.db import transaction
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


class VMCashManager(AbstractCashManager):
    def return_coins(self,return_summ):
        return_coins_str = ""

        # get coins with its count, in vending machine bank
        vm_cash_count = dict(((vmc.coin.value, vmc) for vmc in self.select_related('coin').filter(cnt__gt=0)))
        sorted_vmc_keys = sorted(vm_cash_count.keys(), reverse=True)

        for coin_value in sorted_vmc_keys:
            count_coins_to_back = 0
            count_coins_in_vm = vm_cash_count[coin_value].cnt

            remainder = int(return_summ / coin_value)
            if remainder:
                if remainder <= count_coins_in_vm:
                    count_coints_to_back = remainder
                else:
                    count_coints_to_back = remainder - count_coins_in_vm
                return_summ -= count_coints_to_back * coin_value

                with transaction.atomic():
                    coin = vm_cash_count[coin_value].coin
                    u_cash = UserCash.objects.get_or_none(coin=coin)
                    if u_cash:
                        u_cash.cnt += count_coints_to_back
                        vm_cash_count[coin_value].cnt -= count_coints_to_back
                        u_cash.save()
                        vm_cash_count[coin_value].save()

                        return_coins_str += str(coin_value) + "р. : " + str(count_coints_to_back) + "шт; "
            # ----------------------------------------------------------

        return return_coins_str,return_summ

class VMCash(AbstractCash):
    objects = VMCashManager()
    class Meta:
        verbose_name ="деньги машины"
        verbose_name_plural = "деньги машины"

class UserVMCashManager(AbstractCashManager):
    def move_all_to_vending(self):
        for uvm_cash in self.filter(cnt__gt=0):
            vm_cash = VMCash.objects.get_or_none(coin_id=uvm_cash.coin_id)
            if vm_cash:
                with transaction.atomic():
                    vm_cash.cnt += uvm_cash.cnt
                    uvm_cash.cnt = 0
                    vm_cash.save()
                    uvm_cash.save()

    def move_summ_to_vending(self,summ):
        uvm_cash_count = dict(((uvm.coin.value, uvm) for uvm in self.select_related('coin').filter(cnt__gt=0)))
        sorted_vmc_keys = sorted(uvm_cash_count.keys(), reverse=True)
        for coin_value in sorted_vmc_keys:
            remainder = int(summ / coin_value)
            uvm_cash = uvm_cash_count[coin_value]
            if summ != 0:

                count_coins_to_vm = uvm_cash.cnt;
                if remainder < uvm_cash.cnt:
                    count_coins_to_vm = remainder

                vm_cash = VMCash.objects.get_or_none(coin=uvm_cash.coin)
                if vm_cash:
                    with transaction.atomic():
                        uvm_cash.cnt -= count_coins_to_vm
                        vm_cash.cnt += count_coins_to_vm
                        uvm_cash.save()
                        vm_cash.save()

                        summ -= coin_value * count_coins_to_vm



class UserVMCash(AbstractCash):
    objects = UserVMCashManager()
    class Meta:
        verbose_name ="активные деньги"
        verbose_name_plural = "активные деньги"

class ProductManager(DefaultManager):
    def get_all_dict(self):
        return dict(((p.id,{
            "id":p.id,
            "title":p.title,
            "price":p.price,
            "count":p.cnt
        }) for p in self.all().order_by('sort')))

class Product(models.Model):
    title = models.CharField('Название', max_length=255)
    cnt = models.PositiveIntegerField('Остаток',default=0)
    price = models.PositiveIntegerField('Сумма',default=0)
    sort = models.PositiveSmallIntegerField('Количество',default=0)
    objects = ProductManager()

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