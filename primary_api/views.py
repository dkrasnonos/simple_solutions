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
        context = {'id': item.id, 'name': item.name, 'description': item.description, 'price': item.price,
                   'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY}

        return render(request, 'item.html', context)


class BuyItem(APIView):

    def get(self, request, *args, **kwargs):
        item = get_object_or_404(Item, pk=kwargs.get('id'))

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'rub',
                    'product_data': {
                        'name': item.name,
                        'description': item.description,
                    },
                    'unit_amount': int(item.price * 100),
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
