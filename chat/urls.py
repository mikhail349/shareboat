from django.urls import path, include
from django.conf.urls import url

from . import views

app_name = 'chat'

apiurlpatterns = [
    path('send_message_booking/<int:pk>/', views.send_message_booking),
    path('get_new_messages_booking/<int:pk>/', views.get_new_messages_booking),

    path('get_new_messages_boat/<int:pk>/', views.get_new_messages_boat),
    path('send_message_boat/<int:pk>/', views.send_message_boat)
]

urlpatterns = [
    path('booking/<int:pk>/', views.booking, name='booking'),
    path('boat/<int:pk>/', views.boat, name='boat'),
    path('api/', include(apiurlpatterns))
]