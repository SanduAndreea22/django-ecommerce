from django.urls import path
from . import views

app_name = 'products'  # Namespacing the app

urlpatterns = [
    path('', views.home, name='home'),  # Home page → latest products
    path('products/', views.product_list, name='product_list'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),
    path('newsletter/subscribe/', views.subscribe_newsletter, name='subscribe_newsletter'),
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),
]
