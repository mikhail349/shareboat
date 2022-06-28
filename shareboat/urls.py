"""shareboat URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls import url

from user import urls as user_urls
from boat import urls as boat_urls
from booking import urls as booking_urls
from telegram_bot import urls as telegram_bot_urls 
from chat import urls as chat_urls
from portal import urls as portal_urls

from . import views
from boat import views as boat_views

urlpatterns = [
    path('', boat_views.search_boats),
    path(f'{settings.ADMIN_URL}/', admin.site.urls),

    path('user/', include(user_urls)),
    path('boats/', include(boat_urls)),
    path('bookings/', include(booking_urls)),
    path('telegram_bot/', include(telegram_bot_urls)),
    path('chat/', include(chat_urls)),
    path('portal/', include(portal_urls)),

    path('summernote/', include('django_summernote.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)