import stripe

from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from primary_api.models import Item, Order, OrderItem
from solutions import settings


class GetItem(APIView):

    def get(self, request, *args, **kwargs):
        item = get_object_or_404(Item, pk=kwargs.get('id'))
        if request.query_params:
            temp_item_currency = request.query_params.get('currency')
            temp_price = item.price
            if item.currency == 'RUB' and temp_item_currency == 'USD':
                temp_price = round(item.price / 90, 2)
            elif item.currency == 'USD' and temp_item_currency == 'RUB':
                temp_price = round(item.price * 90, 2)
            return JsonResponse({'price': temp_price})
        context = {'id': item.id, 'name': item.name, 'description': item.description, 'price': item.price,
                   'currency': item.currency, 'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY}

        return render(request, 'item.html', context)


class BuyItem(APIView):

    def get(self, request, *args, **kwargs):
        item = get_object_or_404(Item, pk=kwargs.get('id'))
        temp_item_currency = item.currency
        temp_price = item.price

        if request.query_params:
            temp_item_currency = request.query_params.get('currency')
            if item.currency == 'RUB' and temp_item_currency == 'USD':
                temp_price = round(item.price / 90, 2)
            elif item.currency == 'USD' and temp_item_currency == 'RUB':
                temp_price = round(item.price * 90, 2)

        if temp_item_currency == 'USD':
            stripe.api_key = settings.STRIPE_SECRET_KEY_USD
        elif temp_item_currency == 'RUB':
            stripe.api_key = settings.STRIPE_SECRET_KEY_RUB
        else:
            # Обработка ошибки, если валюта не поддерживается
            return JsonResponse({'error': 'Выбранная валюта не поддерживается'})
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': temp_item_currency.lower(),
                    'product_data': {
                        'name': item.name,
                        'description': item.description,
                    },
                    'unit_amount': int(temp_price * 100),
                },
                'quantity': 1,
            }],
            cancel_url='http://127.0.0.1:8000',
            success_url='http://127.0.0.1:8000',
            mode='payment',
        )

        return JsonResponse({'sessionId': checkout_session['id']})


class OrderView(APIView):
    def get(self, request, *args, **kwargs):
        tax = ''
        discount = ''
        total_price = ''
        items = list()

        try:
            order = Order.objects.get(id=kwargs.get('id'))
            order_items = OrderItem.objects.filter(order=order)
            for order_item in order_items:
                for i in range (0, order_item.quantity):
                    items.append(order_item.item)


            discount = sum(discount.amount for discount in order.discounts.all())
            taxes = order.taxes.all()
            total_price = order.get_total_price()
        except Exception:
            return JsonResponse({'info': f'Не удалсоь получить данные по заказу {order.id}'}, encoder='utf-8')

        context = {'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY, 'order_id': order.id,
                   'items': items, 'taxes': taxes, 'discount': discount, 'total_price': total_price}
        return render(request, 'order.html', context)


class IntentPayment(APIView):
    def post(self, request):
        order_id = int(request.data['order'][0]['id'])
        try:
            order = Order.objects.get(id=order_id)
            total_price = order.get_total_price()
            items = list()
            order_items = OrderItem.objects.filter(order=order)
            for order_item in order_items:
                for i in range(0, order_item.quantity):
                    items.append(order_item.item)

        except Exception:
            return JsonResponse({'info': 'Заказ не найден или устарел'}, status=400)
        stripe.api_key = settings.STRIPE_SECRET_KEY
        intent = stripe.PaymentIntent.create(
            amount=int(total_price) * 100,
            currency=items[0].currency.lower(),
            payment_method_types=["card"],
        )
        return JsonResponse({'clientSecret': intent.client_secret})
