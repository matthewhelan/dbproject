"""dbproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.login, name='login'),
    path('index/', views.index, name='index'),
    path('players/', views.players, name='players'),
    path('parlays/', views.parlays, name='parlays'),
    path('parlays/active', views.active, name='active'),
    path('parlays/create/', views.create_parlay, name='createparlay'),
    path('parlays/submit/', views.submit_parlay, name='submitparlay'),
    path('parlays/delete_leg/<int:idx>', views.delete_leg, name='deleteleg'),
    path('players/<int:player_id>', views.playerPage, name='playerpage'),
    path('follow/<int:user_id>/', views.follow, name='followUser'),
    path('unfollow/<int:user_id>/', views.unfollow, name="unfollowUser"),
    path('logout/', views.logout_view, name='logout')

]
