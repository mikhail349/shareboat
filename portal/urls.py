from django.urls import path, re_path

from . import views

app_name = 'portal'

urlpatterns = [
    re_path(r'.*', views.portal, name="portal"),
]