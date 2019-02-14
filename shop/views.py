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
            "error":{},
            "message":"..."
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
            UserVMCash.objects.move_all_to_vending()
            # ----------------------------------------------------------

            # try to give coins to user from VMCash to UserCash by larger coins
            # ----------------------------------------------------------
            return_coins_str,user_vm_summ = VMCash.objects.return_coins(user_vm_summ)

            result["user_cash"] = UserCash.objects.get_all_dict()
            result["vm_cash"] = VMCash.objects.get_all_dict()
            result["user_vm_summ"] = user_vm_summ
            result["message"] = "Vending вернул - " + return_coins_str if return_coins_str else "Vending ничего не вернул"
            # ----------------------------------------------------------

        elif action == "buy_product":
            # get user cash summ in vending machine
            user_vm_summ = UserVMCash.objects.get_summ()
            product_id = post_data.get("product_id","")
            if product_id:
                product = Product.objects.get_or_none(pk=int(product_id))
                if product and product.cnt and user_vm_summ >= product.price:
                    UserVMCash.objects.move_all_to_vending()

                    need_to_return = user_vm_summ - product.price
                    return_coins_str,user_vm_summ = VMCash.objects.return_coins(need_to_return)

                    result["message"] = "Вы купили - " + product.title + " "
                    if return_coins_str:
                        result["message"] += return_coins_str
                elif not product or product.cnt == 0:
                    result["message"] = product.title + " - осутствует"
                else:
                    result["message"] = "Недостаточно средств, внесите еще: " + str(product.price - user_vm_summ) + " р."

                result["user_cash"] = UserCash.objects.get_all_dict()
                result["vm_cash"] = VMCash.objects.get_all_dict()

        return JsonResponse(result)


