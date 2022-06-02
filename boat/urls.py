from django.urls import path, include
from django.conf.urls import url

from . import views

app_name = 'boat'

apiurlpatterns = [
    path('create/', views.create, name='api_create'),
    path('update/<int:pk>/', views.update, name='api_update'),
    path('delete/<int:pk>/', views.delete, name='api_delete'),

    path('get_files/<int:pk>/', views.get_files),
    path('calc_booking/<int:pk>/', views.calc_booking, name='api_calc_booking'),
    path('set_status/<int:pk>/', views.set_status, name='api_set_status'),
    path('get_models/<int:pk>/', views.get_models),
    path('switch_fav/<int:pk>/', views.switch_fav)
]

urlpatterns = [
    path('', views.boats, name="boats"),
    path('my_boats/', views.my_boats, name='my_boats'),
    path('boats_on_moderation/', views.boats_on_moderation, name='boats_on_moderation'),

    path('create/', views.create, name='create'),
    path('update/<int:pk>/', views.update, name='update'),
    path('booking/<int:pk>/', views.booking, name='booking'),
    path('view/<int:pk>/', views.view, name='view'),

    path('moderate/<int:pk>/', views.moderate, name='moderate'),
    path('accept/<int:pk>/', views.accept, name='accept'),
    path('reject/<int:pk>/', views.reject, name='reject'),

    path('api/', include(apiurlpatterns))
]