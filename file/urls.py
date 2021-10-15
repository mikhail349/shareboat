from django.urls import path, include
from django.conf.urls import url

from . import views

apiurlpatterns = [
    url(r'get_assetfiles/(?P<pk>[0-9]+)/', views.get_assetfiles),
]

urlpatterns = [
    path('api/', include(apiurlpatterns))
]