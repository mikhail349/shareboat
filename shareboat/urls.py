from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

from user import urls as user_urls
from boat import urls as boat_urls
from booking import urls as booking_urls
from telegram_bot import urls as telegram_bot_urls
from chat import urls as chat_urls
from portal import urls as portal_urls
from . import views


urlpatterns = [
    path('', views.index),
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
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
