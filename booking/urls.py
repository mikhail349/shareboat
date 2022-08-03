from django.urls import path, include
from django.conf.urls import url

from . import views

app_name = 'booking'

apiurlpatterns = [
    path('set_status/<int:pk>/', views.set_status, name='api_set_status'),
    path('set_request_status/<int:pk>/', views.set_request_status, name="api_set_request_status")
]

urlpatterns = [
    path('my_bookings', views.my_bookings, name='my_bookings'),
    path('confirm/<int:boat_pk>/', views.confirm, name='confirm'),
    path('create/', views.create, name='create'),
    path('requests', views.requests, name='requests'),
    path('view/<int:pk>/', views.view, name='view'),
    path('api/', include(apiurlpatterns))
]