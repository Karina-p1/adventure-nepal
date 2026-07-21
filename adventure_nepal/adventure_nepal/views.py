from django.shortcuts import render


def home(request):
    context = {"page_title": "Home"}
    return render(request, "pages/home.html", context)


def about(request):
    return render(request, "pages/about.html")