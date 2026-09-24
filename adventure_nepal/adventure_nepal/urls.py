from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from adventure_nepal import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("", include("apps.core.urls")),
    path("treks/", include("apps.treks.urls")),
    path("guides/", include("apps.guides.urls")),
    path("accounts/", include("apps.accounts.urls")),
    path("bookings/", include("apps.bookings.urls")),
    path("reviews/", include("apps.reviews.urls")),
    path("contact/", include("apps.contact.urls")),
]

if settings.DEBUG:
    # runserver already serves static files; only media needs a route.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)