from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('cash/<str:order_number>/', views.cash_payment, name='cash_payment'),
]
