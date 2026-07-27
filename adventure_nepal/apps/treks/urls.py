from django.urls import path
from . import views

app_name = "treks"

urlpatterns = [
    path("", views.trek_list, name="list"),
    path("<slug:slug>/", views.trek_detail, name="detail"),
]