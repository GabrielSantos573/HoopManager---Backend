from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.get_times, name="get_times"),
    path('get_times/', views.get_times, name="get_times"),
    path("get_jogadores/<int:time_id>/", views.get_jogadores, name="get_jogadores"),
    path("create_time/", views.create_time, name="create_time"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
