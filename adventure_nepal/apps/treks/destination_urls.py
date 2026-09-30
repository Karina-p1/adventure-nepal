from django.urls import path

from . import destination_views as views

app_name = "destinations"

urlpatterns = [
    path("", views.destination_list, name="list"),
    path("<slug:slug>/", views.destination_detail, name="detail"),
]