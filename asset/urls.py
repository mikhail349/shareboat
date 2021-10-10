from django.urls import path, include

from . import views

apiurlpatterns = [
    path('delete/', views.delete),
]

urlpatterns = [
    path('', views.get, name='get'),
    path('create/', views.create, name='create'),

    path('api/', include(apiurlpatterns))
]