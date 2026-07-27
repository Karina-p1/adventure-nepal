from django.shortcuts import render, get_object_or_404
from apps.accounts.models import CustomUser


def guide_list(request):
    guides = CustomUser.objects.filter(
        role=CustomUser.Role.GUIDE, is_active=True
    ).select_related("guide_profile")
    context = {"guides": guides}
    return render(request, "guides/guide_list.html", context)


def guide_detail(request, pk):
    guide = get_object_or_404(
        CustomUser.objects.select_related("guide_profile").prefetch_related("treks_guided"),
        pk=pk, role=CustomUser.Role.GUIDE, is_active=True
    )
    context = {"guide": guide}
    return render(request, "guides/guide_detail.html", context)