from django.urls import path, include
from django.conf.urls import url

from . import views

app_name = 'booking'

apiurlpatterns = [
    path('create/', views.create, name='api_create'),
]

urlpatterns = [
    path('my_bookings', views.my_bookings, name='my_bookings'),
    path('api/', include(apiurlpatterns))
]