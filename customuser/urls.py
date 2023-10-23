# customuser/urls.py
from django.urls import path
from django.contrib.auth.views import LoginView

from . import views

urlpatterns = [
    path('otp-verification/', views.otp_verification, name='otp_verification'),
    path('medallion/portal/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('resend-otp/', views.resend_otp_view, name='resend-otp'),
    path('terms_of_service/', views.view_terms_of_service, name='terms_of_service'),
    # path('accounts/login/', LoginView.as_view(), name='login'),
    # path('accounts/login/', views.custom_login, name='custom_login'),
]
