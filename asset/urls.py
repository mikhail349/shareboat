from django.urls import path, include
from django.conf.urls import url

from . import views

apiurlpatterns = [
    url(r'delete/(?P<pk>[0-9]+)/', views.delete),
]

urlpatterns = [
    path('', views.get, name='get'),
    path('create/', views.create, name='create'),

    path('api/', include(apiurlpatterns))
]