from django.urls import path

from . import views


app_name = "dashboard"


urlpatterns = [
    # ========================================================
    # DASHBOARD
    # ========================================================
    path(
        "",
        views.dashboard_home,
        name="home",
    ),

    # ========================================================
    # BOOKINGS
    # ========================================================
    path(
        "bookings/",
        views.booking_list,
        name="booking_list",
    ),

    path(
        "bookings/<int:pk>/",
        views.booking_detail,
        name="booking_detail",
    ),

    path(
        "bookings/<int:pk>/status/<str:action>/",
        views.booking_status_action,
        name="booking_status_action",
    ),

    path(
        "bookings/<int:pk>/payment/",
        views.booking_payment_update,
        name="booking_payment_update",
    ),

    # ========================================================
    # TREKS
    # ========================================================
    path(
        "treks/",
        views.trek_manage_list,
        name="trek_list",
    ),

    path(
        "treks/add/",
        views.trek_create,
        name="trek_create",
    ),

    path(
        "treks/<int:pk>/edit/",
        views.trek_edit,
        name="trek_edit",
    ),

    path(
        "treks/<int:pk>/toggle/",
        views.trek_toggle_active,
        name="trek_toggle_active",
    ),

    # ========================================================
    # DESTINATIONS
    # ========================================================
    path(
        "destinations/",
        views.destination_manage_list,
        name="destination_list",
    ),

    path(
        "destinations/add/",
        views.destination_create,
        name="destination_create",
    ),

    path(
        "destinations/<int:pk>/edit/",
        views.destination_edit,
        name="destination_edit",
    ),
]