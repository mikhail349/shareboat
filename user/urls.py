from rest_framework_jwt.views import obtain_jwt_token
from django.conf.urls import url
from django.urls import path, include

from . import views 

urlapipatterns = [
    url('get_token/', obtain_jwt_token),
    path('update/', views.update, name='profile'),
]

urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
    path('update/', views.update, name='update'),
    
    path('api/', include(urlapipatterns))
]