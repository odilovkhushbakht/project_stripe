import json

import stripe
from django.db import connection

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView, DetailView
from app_pay import settings
from api.models import Item, Order

stripe.api_key = settings.API_SEC_KEY


def successView(request):
    return render(request=request, template_name="success/success.html", status=200)


def cancelView(request):
    return HttpResponse(content="cancel", status=200)


class BuyView(ListView):
    model = Item

    def get_queryset(self):
        return Item.objects.get(pk=self.kwargs['pk'])

    def get(self, request, *args, **kwargs):
        product = self.get_queryset()
        line_items = [
            {
                'quantity': 1,
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': product.price,
                    'product_data': {
                        'name': product.name,
                        'description': product.description,
                    },
                },
            },
        ]
        mode = "payment"
        host = 'http://localhost:8000'
        success_url = f'{host}{reverse("success")}'  # 'http://localhost:8000/api/v1/success'
        cancel_url = f'{host}{reverse("cancel")}'  # 'http://localhost:8000/api/v1/cancel'
        try:
            session = stripe.checkout.Session.create(
                line_items=line_items,
                mode=mode,
                success_url=success_url,
                cancel_url=cancel_url,
            )
            content_res = "%s%s%s" % ('{"id":"', str(session.id).__str__(), '"}')
        except Exception:
            content_res = '{"id": "error"}'
        return JsonResponse(data=content_res)


class ItemView(DetailView):
    model = Item
    pk_url_kwarg = 'id'
    context_object_name = "item"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['api_pub_key'] = settings.API_PUB_KEY
        return context


class OrderBuyView(ListView):
    model = Order
    pk_url_kwarg = 'order_num'
    context_object_name = 'order'

    def get_queryset(self):
        try:
            return Order.objects.filter(order_num=self.kwargs['order_num'])
        except KeyError:
            return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['api_pub_key'] = settings.API_PUB_KEY
        line_items = []
        order = self.get_queryset()
        for item in order:
            line_items.append(
                {
                    'quantity': item.quantity,
                    'price_data': {
                        'currency': item.product_num.currency,
                        'unit_amount': item.product_num.price,
                        'product_data': {
                            'name': item.product_num.name,
                            'description': item.product_num.description,
                        },
                    },
                }
            )
        mode = "payment"
        host = 'http://localhost:8000'
        success_url = f'{host}{reverse("success")}'  # 'http://localhost:8000/api/v1/success'
        cancel_url = f'{host}{reverse("cancel")}'  # 'http://localhost:8000/api/v1/cancel'
        session = stripe.checkout.Session.create(
            line_items=line_items,
            mode=mode,
            success_url=success_url,
            cancel_url=cancel_url,
        )
        context['session_id'] = session.id
        return context


@require_http_methods(['GET'])
def order_view(request, **kwargs):
    order = list(Order.objects.all().values())
    return JsonResponse(data=order, safe=False)


@require_http_methods(['GET'])
def order_by_id_view(request, **kwargs):
    try:
        order = list(Order.objects.filter(order_num=kwargs['id']).values())
        return JsonResponse(data=order, safe=False)
    except KeyError:
        return JsonResponse(data={"message": "json key error"})


@require_http_methods(['POST'])
@csrf_exempt  # отключить CSRF
def order_add_view(request):
    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse(data={"message": "json error"})
    try:
        order_id = data['order'][0]['id']
        products_status = []
        for item in data.get('product'):
            product = Item.objects.filter(pk=item['product_id'])
            if product.exists():
                default_dict = {'order_num': order_id, 'product_num': product[0]}
                order_obj, status_query = Order.objects.get_or_create(order_num=order_id,
                                                                      product_num=item['product_id'],
                                                                      defaults=default_dict)
                if status_query:
                    order_obj.quantity = item['quantity']
                else:
                    order_obj.quantity = order_obj.quantity + int(item['quantity'])
                    order_obj.save()
                products_status.append({"id": order_obj.id, "status": "success"})
            else:
                products_status.append({"id": product.id, "message": "not found"})
        return JsonResponse(data=products_status, safe=False)
    except KeyError:
        return JsonResponse(data={"message": "json key error"})


@require_http_methods(['DELETE'])
@csrf_exempt  # отключить CSRF
def order_delete_view(request, **kwargs):
    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse(data={"message": "json error"})
    try:
        raw_sql = f'Delete From api_order Where order_num={data["order_id"]}'
        with connection.cursor() as cursor:
            cursor.execute(raw_sql)
        return JsonResponse(data={"message": "success"})
    except KeyError:
        return JsonResponse(data={"message": "json key error"})


@require_http_methods(['DELETE'])
@csrf_exempt  # отключить CSRF
def order_product_delete_view(request, **kwargs):
    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse(data={"message": "json error"})
    try:
        i = 0
        raw_sql = f'Delete From api_order Where order_num={data["order_id"]} AND'
        for item in data['product']:
            if i == 0:
                raw_sql = f'{raw_sql} product_num_id={item["product_id"]}'
            else:
                raw_sql = f'{raw_sql} OR product_num_id={item["product_id"]}'
            i = + 1
        with connection.cursor() as cursor:
            cursor.execute(raw_sql)
        return JsonResponse(data={"message": "success"})
    except KeyError:
        return JsonResponse(data={"message": "json key error"})
