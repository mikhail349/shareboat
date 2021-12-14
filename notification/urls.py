from django.urls import path, include
from django.conf.urls import url

from . import views

app_name = 'notification'

apiurlpatterns = [
    path('delete/<int:pk>/', views.delete, name='api_delete'),
    path('delete_all/', views.delete_all, name='api_delete_all')
]

urlpatterns = [
    path('api/', include(apiurlpatterns)),
]