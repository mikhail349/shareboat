from django.urls import path, include
from django.conf.urls import url

from . import views

apiurlpatterns = [
    path('create/', views.create, name='create'),
    url(r'delete/(?P<pk>[0-9]+)/', views.delete),
]

urlpatterns = [
    path('', views.get, name='get'),
    path('create/', views.create, name='create'),
    url(r'update/(?P<pk>[0-9]+)/', views.update, name='update'),

    path('api/', include(apiurlpatterns))
]