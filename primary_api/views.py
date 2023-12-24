import stripe

from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from primary_api.models import Item
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


class Order(APIView):
    def get(self, request, *args, **kwargs):
        context = {'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY}
        return render(request, 'order.html', context)


class IntentPayment(APIView):
    def post(self, request):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        intent = stripe.PaymentIntent.create(
            amount=1099,
            currency="usd",
            payment_method_types=["card"],
        )
        return JsonResponse({'clientSecret': intent.client_secret})
