"""apps URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('grade/', views.grade, name='grade'),
    path('add/', views.add_apps, name='add'),
    path('stats/', views.stats, name='stats'),
    path('manage/', views.manage, name='manage'),
    path('export_graded/', views.export_graded, name='export_graded'),
    path('export_accepted/', views.export_accepted, name='export_accepted'),
    path('export_rejected/', views.export_rejected, name='export_rejected'),
    path('export_waitlisted/', views.export_waitlisted, name='export_waitlisted'),
    path('export_total/', views.export_total, name='export_total'),
    path('clear/', views.clear, name='clear'),
]
