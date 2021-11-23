from django.urls import path, include
from django.conf.urls import url

from . import views

app_name = 'boat'

apiurlpatterns = [
    path('create/', views.create, name='api_create'),
    url(r'delete/(?P<pk>[0-9]+)/', views.delete, name='api_delete'),
    url(r'get_files/(?P<pk>[0-9]+)/', views.get_files),
    path('calc_booking/<int:pk>/', views.calc_booking, name='api_calc_booking')
]

urlpatterns = [
    path('', views.boats, name="boats"),
    path('my_boats/', views.my_boats, name='my_boats'),

    path('create/', views.create, name='create'),
    url(r'update/(?P<pk>[0-9]+)/', views.update, name='update'),
    path('booking/<int:pk>/', views.booking, name='booking'),

    path('api/', include(apiurlpatterns))
]