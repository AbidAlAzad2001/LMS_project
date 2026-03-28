from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart_view, name='cart_view'),
    path('add/<int:course_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:course_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('clear/', views.clear_cart, name='clear_cart'),
    path('checkout/', views.checkout, name='cart_checkout'),
    path('summary/', views.cart_summary, name='cart_summary'),
]
