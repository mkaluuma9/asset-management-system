from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    #path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('request/', views.make_asset_request, name='make_request'),
    path('assets/', views.view_assigned_assets, name='view_assets'),
    path('payment/', views.make_payment, name='make_payment'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),


]
