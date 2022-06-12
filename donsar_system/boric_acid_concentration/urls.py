"""donsar_system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from . import views
from django.urls import path

urlpatterns = [
    path('', views.bor_calc_resume_page, name='bor_calc'),
    path('start_calc/', views.bor_calc_start_page, name='bor_calc_start'),
    path('add_album/', views.add_album_page, name='add_album'),
    path('graph/', views.graph_page, name='graph'),
    path('add_points/', views.add_points, name='add_points'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_user, name='logout')
]
