from django.urls import path, include
from django.conf.urls import url

from . import views

app_name = 'chat'

apiurlpatterns = [
    path('send_message_booking/', views.send_message_booking),
]

urlpatterns = [
    path('booking/<int:pk>/', views.booking, name='booking'),
    path('api/', include(apiurlpatterns))
]