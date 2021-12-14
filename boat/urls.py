from django.urls import path, include
from django.conf.urls import url

from . import views

app_name = 'boat'

apiurlpatterns = [
    path('create/', views.create, name='api_create'),
    url(r'delete/(?P<pk>[0-9]+)/', views.delete, name='api_delete'),
    url(r'get_files/(?P<pk>[0-9]+)/', views.get_files),
    path('calc_booking/<int:pk>/', views.calc_booking, name='api_calc_booking'),
    path('set_status/<int:pk>/', views.set_status, name='api_set_status'),

    path('decline_boat/<int:pk>/', views.decline_boat, name='api_decline_boat'),
    path('accept_boat/<int:pk>/', views.accept_boat, name='api_accept_boat')
]

urlpatterns = [
    path('', views.boats, name="boats"),
    path('my_boats/', views.my_boats, name='my_boats'),
    path('boats_on_moderation/', views.boats_on_moderation, name='boats_on_moderation'),

    path('create/', views.create, name='create'),
    url(r'update/(?P<pk>[0-9]+)/', views.update, name='update'),
    path('booking/<int:pk>/', views.booking, name='booking'),
    path('view/<int:pk>/', views.view, name='view'),
    path('moderate/<int:pk>/', views.moderate, name='moderate'),
    path('api/', include(apiurlpatterns))
]