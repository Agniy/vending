import json

from django.views.generic import TemplateView
from django.http import JsonResponse
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from shop.models import Product,UserCash,VMCash,UserVMCash,Order

class IndexView(TemplateView):
    template_name = "index.html"

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(IndexView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        
        context['json_products'] = json.dumps(Product.objects.get_all_dict())
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
                    return_coins_str = ""
                    user_vm_summ = 0
                    if need_to_return:
                        return_coins_str,user_vm_summ = VMCash.objects.return_coins(need_to_return)

                    #decrease count of products
                    product.cnt-=1
                    product.save()

                    #create Order
                    order = Order.objects.create(product=product,count=1,summ=product.price)

                    result["message"] = "Заказ №"+ str(order.id) + ". Вы купили - " + product.title + ". "
                    if return_coins_str:
                        result["message"] += "Vending вернул - " + return_coins_str
                elif not product or product.cnt == 0:
                    result["message"] = product.title + " - осутствует"
                else:
                    result["message"] = "Недостаточно средств, внесите еще: " + str(product.price - user_vm_summ) + " р."

            result["user_cash"] = UserCash.objects.get_all_dict()
            result["vm_cash"] = VMCash.objects.get_all_dict()
            result["products"] = Product.objects.get_all_dict()
            result["user_vm_summ"] = user_vm_summ

        return JsonResponse(result)


