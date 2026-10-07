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
# ============================================================
# DESTINATIONS
# ============================================================

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


# ============================================================
# CUSTOMERS
# ============================================================

path(
    "customers/",
    views.customer_list,
    name="customer_list",
),

path(
    "customers/<int:pk>/",
    views.customer_detail,
    name="customer_detail",
),

path(
    "customers/<int:pk>/toggle-active/",
    views.customer_toggle_active,
    name="customer_toggle_active",
),


# ============================================================
# GUIDES
# ============================================================

path(
    "guides/",
    views.guide_manage_list,
    name="guide_list",
),

path(
    "guides/<int:pk>/",
    views.guide_manage_detail,
    name="guide_detail",
),

path(
    "guides/<int:pk>/edit/",
    views.guide_manage_edit,
    name="guide_edit",
),

path(
    "guides/<int:pk>/toggle-active/",
    views.guide_toggle_active,
    name="guide_toggle_active",
),

path(
    "guides/<int:pk>/toggle-public/",
    views.guide_toggle_public,
    name="guide_toggle_public",
),
# ============================================================
# REVIEWS
# ============================================================

path(
    "reviews/",
    views.review_manage_list,
    name="review_list",
),

path(
    "reviews/<int:pk>/",
    views.review_manage_detail,
    name="review_detail",
),

path(
    "reviews/<int:pk>/toggle/",
    views.review_toggle_approval,
    name="review_toggle_approval",
),
# ============================================================
# INQUIRIES
# ============================================================

path(
    "inquiries/",
    views.inquiry_manage_list,
    name="inquiry_list",
),

path(
    "inquiries/<int:pk>/",
    views.inquiry_manage_detail,
    name="inquiry_detail",
),

path(
    "inquiries/<int:pk>/toggle-resolved/",
    views.inquiry_toggle_resolved,
    name="inquiry_toggle_resolved",
),
# ============================================================
# CUSTOM TRIP REQUESTS
# ============================================================

path(
    "custom-trips/",
    views.custom_trip_manage_list,
    name="custom_trip_list",
),

path(
    "custom-trips/<int:pk>/",
    views.custom_trip_manage_detail,
    name="custom_trip_detail",
),

path(
    "custom-trips/<int:pk>/status/",
    views.custom_trip_status_update,
    name="custom_trip_status_update",
),]