from django.urls import path, include
from django.conf.urls import url

from . import views

app_name = 'boat'

apiurlpatterns = [
    path('create/', views.create, name='api_create'),
    url(r'delete/(?P<pk>[0-9]+)/', views.delete),
    url(r'get_files/(?P<pk>[0-9]+)/', views.get_files),
]

urlpatterns = [
    path('', views.get, name='boats'),
    path('create/', views.create, name='create'),
    url(r'update/(?P<pk>[0-9]+)/', views.update, name='update'),

    path('api/', include(apiurlpatterns))
]