# from django.contrib import admin
from django.urls import path
from .views import *



urlpatterns = [
    path('', index, name='anasayfa'),
    path('home/', Home, name='home'),
    path('stop_camera/', stop_camera, name='stop_camera'),
    path('game/', game, name='game'),
]
