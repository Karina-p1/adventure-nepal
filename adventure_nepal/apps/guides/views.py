from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, render

from apps.accounts.models import CustomUser
from apps.treks.models import Trek


def guide_list(request):
    guides = CustomUser.objects.filter(role=CustomUser.Role.GUIDE, is_active=True).select_related("guide_profile")
    return render(request, "guides/guide_list.html", {"guides": guides})


def guide_detail(request, pk):
    guide = get_object_or_404(
        CustomUser.objects.select_related("guide_profile").prefetch_related(
            Prefetch("guided_treks", queryset=Trek.objects.filter(is_active=True).select_related("region"))
        ),
        pk=pk, role=CustomUser.Role.GUIDE, is_active=True,
    )
    return render(request, "guides/guide_detail.html", {"guide": guide})