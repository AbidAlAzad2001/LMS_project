from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('verify/<str:token>/', views.verify_email, name='verify_email'),
    path('resend-verification/', views.resend_verification, name='resend_verification'),
]
