from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('cash/<str:order_number>/', views.cash_payment, name='cash_payment'),
    path('stripe/checkout/<str:order_number>/', views.stripe_checkout, name='stripe_checkout'),
    path('stripe/success/<str:order_number>/', views.stripe_success, name='stripe_success'),
    path('stripe/cancel/<str:order_number>/', views.stripe_cancel, name='stripe_cancel'),
    path('stripe/webhook/', views.stripe_webhook, name='stripe_webhook'),
]
