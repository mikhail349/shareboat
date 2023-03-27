from django.urls import include, path

from . import views

app_name = 'boat'

apiurlpatterns = [
    path('create/', views.create, name='api_create'),
    path('update/<int:pk>/', views.update, name='api_update'),
    path('delete/<int:pk>/', views.delete, name='api_delete'),

    path('get_files/<int:pk>/', views.get_files, name='api_get_files'),
    path('calc_booking/<int:pk>/', views.calc_booking,
         name='api_calc_booking'),
    path('set_status/<int:pk>/', views.set_status, name='api_set_status'),
    path('get_models/<int:pk>/', views.get_models, name='api_get_models'),
    path('switch_fav/<int:pk>/', views.switch_fav, name='api_switch_fav')
]

urlpatterns = [
    path('my_boats/', views.my_boats, name='my_boats'),
    path('boats_on_moderation/', views.boats_on_moderation,
         name='boats_on_moderation'),
    path('favs/', views.favs, name='favs'),

    path('create/', views.create, name='create'),
    path('update/<int:pk>/', views.update, name='update'),
    path('booking/<int:pk>/', views.booking, name='booking'),
    path('view/<int:pk>/', views.view, name='view'),

    path('moderate/<int:pk>/', views.moderate, name='moderate'),
    path('accept/<int:pk>/', views.accept, name='accept'),
    path('reject/<int:pk>/', views.reject, name='reject'),
    path('search_boats/', views.search_boats, name='search_boats'),

    path('create_tariff/', views.create_tariff, name='create_tariff'),
    path('update_tariff/<int:pk>/', views.update_tariff, name='update_tariff'),
    path('delete_tariff/<int:pk>/', views.delete_tariff, name='delete_tariff'),

    path('terms/', views.terms, name='terms'),
    path('create_term/', views.create_term, name='create_term'),
    path('update_term/<int:pk>/', views.update_term, name='update_term'),
    path('delete_term/<int:pk>/', views.delete_term, name='delete_term'),

    path('api/', include(apiurlpatterns))
]
