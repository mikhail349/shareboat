from django.urls import path, include
from django.conf.urls import url

from . import views

app_name = 'chat'

apiurlpatterns = [
    path('send_message_booking/<int:pk>/', views.send_message_booking),
    path('get_new_messages_booking/<int:pk>/', views.get_new_messages_booking),

    path('get_new_messages_boat/<int:pk>/', views.get_new_messages_boat),
    path('send_message_boat/<int:pk>/', views.send_message_boat),

    path('get_new_messages/', views.get_new_messages),
    path('send_message/', views.send_message),

    path('get_new_support_messages/<int:user_pk>/',
         views.get_new_support_messages),
    path('send_support_message/<int:user_pk>/', views.send_support_message)
]

urlpatterns = [
    path('booking/<int:pk>/', views.booking, name='booking'),
    path('boat/<int:pk>/', views.boat, name='boat'),
    path('message/', views.message, name='message'),
    path('list/', views.list, name='list'),
    path('support/', views.support, name='support'),
    path('support_chat/<int:user_pk>/', views.support_chat, name='support_chat'),
    path('read_all/', views.read_all, name='read_all'),

    path('api/', include(apiurlpatterns))
]
