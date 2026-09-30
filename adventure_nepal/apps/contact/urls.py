from django.urls import path

from . import views

app_name = "contact"

urlpatterns = [
    path("", views.contact_view, name="contact"),
    path("custom-trip/", views.custom_trip_view, name="custom_trip"),
]