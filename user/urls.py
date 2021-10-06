from rest_framework_jwt.views import obtain_jwt_token
from django.conf.urls import url
from django.urls import path

from . import views 

urlpatterns = [
    path('login/', views.login, name='login'),
    url(r'api/get_token/', obtain_jwt_token),
    url(r'api/auth/', views.auth)
    
]