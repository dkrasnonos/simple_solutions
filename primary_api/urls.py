from django.urls import path
from . import views

urlpatterns = [
    path("buy/<int:id>", views.BuyItem.as_view(), name='buy_item'),
    path("item/<int:id>", views.GetItem.as_view(), name='get_item'),
    path("order/<int:id>", views.Order.as_view(), name='order'),
    path("intent/", views.IntentPayment.as_view(), name='intent'),
]