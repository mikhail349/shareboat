from rest_framework_jwt.views import obtain_jwt_token
from django.conf.urls import url
from django.urls import path, include

from . import views 

app_name = "user"

urlapipatterns = [
    #url('get_token/', obtain_jwt_token),
    path('update/', views.update, name='api_update'),
    path('send_verification_email/', views.send_verification_email, name="send_verification_email")
]

urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
    path('update/', views.update, name='update'),
    path('verify/<uidb64>/<token>/', views.verify, name='verify'),
    
    path('api/', include(urlapipatterns))
]