from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('verify/', views.verify_otp_view, name='verify_otp'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('tickets/create/', views.create_ticket_view, name='create_ticket'),
    path('logout/', views.logout_view, name='logout'),
]
