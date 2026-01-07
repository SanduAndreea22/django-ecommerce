from django.urls import path
from . import views

app_name = 'products'  # Namespacing the app

urlpatterns = [
    path('', views.home, name='home'),  # Home page → latest products
    path('products/', views.product_list, name='product_list'),
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),
]
