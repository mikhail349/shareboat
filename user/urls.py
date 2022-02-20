from django.urls import path, include
from . import views 

app_name = "user"

urlapipatterns = [
    path('update/', views.update, name='api_update'),
    path('send_verification_email/', views.send_verification_email, name="send_verification_email"),
    path('send_restore_password_email/', views.send_restore_password_email, name="send_restore_password_email"),
    path('generate_telegram_code/', views.generate_telegram_code)
]

urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
    path('update/', views.update, name='update'),
    path('restore_password/', views.restore_password, name='restore_password'),

    path('verify/<token>/', views.verify, name='verify'),
    path('change_password/<token>/', views.change_password, name='change_password'),
    path('api/', include(urlapipatterns))
]