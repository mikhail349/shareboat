from django.urls import path, include
from django.conf.urls import url

from . import views

app_name = 'booking'

apiurlpatterns = [
    path('create/', views.create, name='api_create'),
    path('set_status/<int:pk>/', views.set_status, name='api_set_status'),
    path('set_request_status/<int:pk>/', views.set_request_status, name="api_set_request_status")
]

urlpatterns = [
    path('my_bookings', views.my_bookings, name='my_bookings'),
    path('requests', views.requests, name='requests'),
    path('view/<int:pk>/', views.view, name='view'),
    path('api/', include(apiurlpatterns))
]