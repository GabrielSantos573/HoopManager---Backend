from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('get_times/', views.get_times, name="get_times"),
]
