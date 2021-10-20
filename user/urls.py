from rest_framework_jwt.views import obtain_jwt_token
from django.conf.urls import url
from django.urls import path, include

from . import views 

urlapipatterns = [
    url('get_token/', obtain_jwt_token),
]

urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    
    path('api/', include(urlapipatterns))
]