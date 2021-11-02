from django.urls import path, include
from django.conf.urls import url

from . import views

app_name = 'post'

apiurlpatterns = [
    path('create/', views.create, name='api_create'),
    path('update/<int:pk>/', views.update, name='api_update'),
    path('delete/<int:pk>/', views.delete, name='api_delete'),
]

urlpatterns = [
    path('my_posts/', views.my_posts, name='my_posts'),
    path('create/', views.create, name='create'),
    path('update/<int:pk>/', views.update, name='update'),

    path('api/', include(apiurlpatterns))
]