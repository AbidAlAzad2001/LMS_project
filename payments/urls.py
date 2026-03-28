from django.urls import path
from . import views

urlpatterns = [
    path('checkout/<int:course_id>/', views.checkout, name='checkout'),
    path('initiate/<int:course_id>/', views.initiate_payment, name='initiate_payment'),
    path('success/', views.payment_success, name='payment_success'),
    path('fail/', views.payment_fail, name='payment_fail'),
    path('cancel/', views.payment_cancel, name='payment_cancel'),
    path('ipn/', views.payment_ipn, name='payment_ipn'),
    path('demo/otp/', views.demo_payment_otp, name='demo_payment_otp'),
    path('demo/verify/', views.demo_payment_verify, name='demo_payment_verify'),
]
