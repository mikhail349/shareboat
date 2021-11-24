from django.urls import path, include
from django.conf.urls import url

from . import views

app_name = 'booking'

apiurlpatterns = [
    path('create/', views.create, name='api_create'),
]

urlpatterns = [
    #path('my_boats/', views.my_boats, name='my_boats'),
    path('api/', include(apiurlpatterns))
]