from django.urls import path
from . import views

app_name = "bookings"

urlpatterns = [
    path("book/<slug:slug>/", views.create_booking, name="create"),
    path("confirmation/<int:pk>/", views.booking_confirmation, name="confirmation"),
    path("my-bookings/", views.my_bookings, name="my_bookings"),
]