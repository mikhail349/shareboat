from django.urls import path

from . import views

urlpatterns = [
    path('', views.get, name='get'),
    path('my/', views.get_my, name='get_my'),
]