import json

from django.views.generic import TemplateView
from django.http import JsonResponse
from django.db import transaction

from shop.models import Product,UserCash,VMCash,UserVMCash

class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        
        context['json_products'] = json.dumps(dict(((p.id,{
            "id":p.id,
            "title":p.title,
            "price":p.price,
            "count":p.cnt
        }) for p in Product.objects.all().order_by('sort'))))

        context['json_user_cash'] = json.dumps(UserCash.objects.get_all_dict())
        context['json_machine_cash'] = json.dumps(VMCash.objects.get_all_dict())

        context['user_vm_summ'] = UserVMCash.objects.get_summ()

        return context

    def post(self, request, **kwargs):
        result = {
            "success":True,
            "error":{}
        }

        post_data = request.POST
        action = post_data.get("action","")

        if action == "put_coin":
            cash_id = post_data.get("cash_id","")
            if cash_id:
                with transaction.atomic():
                    #reduce count in UserCash
                    user_cash = UserCash.objects.get(pk=int(cash_id))
                    if user_cash.cnt > 0:
                        user_cash.cnt -= 1
                        user_cash.save()

                        #increase count in UserVMCash
                        user_vm_cash,created = UserVMCash.objects.get_or_create(coin=user_cash.coin)
                        user_vm_cash.cnt += 1
                        user_vm_cash.save()

                    result["user_vm_count"] = user_cash.cnt
                result["user_vm_summ"] = UserVMCash.objects.get_summ()
        elif action == "return_coin":

            # get user cash summ in vending machine
            user_vm_summ = UserVMCash.objects.get_summ()

            # move all coins from UserVMCash to VMCash
            # ----------------------------------------------------------
            for uvm_cash in UserVMCash.objects.filter(cnt__gt=0):
                vm_cash = VMCash.objects.get_or_none(coin_id=uvm_cash.coin_id)
                if vm_cash:
                    with transaction.atomic():
                        vm_cash.cnt += uvm_cash.cnt
                        uvm_cash.cnt = 0
                        vm_cash.save()
                        uvm_cash.save()
            # ----------------------------------------------------------

            # try to give coins to user UserCash from VMCash by larger coins
            # ----------------------------------------------------------
            return_coins_str = ""
            # get coins with its count, in vending machine bank
            vm_cash_count = dict(((vmc.coin.value, vmc) for vmc in VMCash.objects.select_related('coin').filter(cnt__gt=0)))
            sorted_vmc_keys = sorted(vm_cash_count.keys(),reverse=True)

            for coin_value in sorted_vmc_keys:
                count_coins_to_back = 0
                count_coins_in_vm = vm_cash_count[coin_value].cnt

                remainder = int(user_vm_summ/coin_value)
                if remainder:
                    if remainder <= count_coins_in_vm:
                        count_coints_to_back = remainder
                    else:
                        count_coints_to_back = remainder - count_coins_in_vm
                    user_vm_summ -= count_coints_to_back * coin_value

                    with transaction.atomic():
                        coin = vm_cash_count[coin_value].coin
                        u_cash = UserCash.objects.get_or_none(coin=coin)
                        if u_cash:
                            u_cash.cnt += count_coints_to_back
                            vm_cash_count[coin_value].cnt -= count_coints_to_back
                            u_cash.save()
                            vm_cash_count[coin_value].save()

                            return_coins_str += str(coin_value) + ":" + str(count_coints_to_back) + "шт; "
                # ----------------------------------------------------------



            result["user_cash"] = UserCash.objects.get_all_dict()
            result["vm_cash"] = VMCash.objects.get_all_dict()
            result["user_vm_summ"] = user_vm_summ
            result["return_coins_str"] = "Автомат вернул - " + return_coins_str if return_coins_str else "Автомат ничего не вернул"
            # ----------------------------------------------------------

        elif action == "buy_product":
            pass

        return JsonResponse(result)


