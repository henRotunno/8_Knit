import json

from django.http import JsonResponse, HttpResponse
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from activities.models import Activities, User


# ==========================================
# PUBLIC API (For Part 3.1 & Vega-Lite 3.2)
# ==========================================
def activity_category_summary(request):
    """
    PUBLIC endpoint: No login required.
    Returns clean JSON aggregate of activity categories and counts.
    """
    data = list(
        Activities.objects
        .values("category")
        .annotate(count=Count("activity_id"))
        .order_by("category")
    )

    return JsonResponse(data, safe=False)


def activities_api(request):
    query = request.GET.get("q", "")

    activities = Activities.objects.all()

    if query:
        activities = activities.filter(activity_name__icontains=query)

    data = list(
        activities.values(
            "activity_id",
            "activity_name",
        )
    )

    return JsonResponse(data, safe=False)


def activities_http_api(request):
    activities = Activities.objects.all()

    data = list(
        activities.values(
            "activity_id",
            "activity_name",
        )
    )

    return HttpResponse(
        json.dumps(data),
        content_type="text/plain"
    )


# ==========================================
# PROTECTED API (Demonstrates auth protection)
# ==========================================
@login_required
def user_friend_summary(request):
    """
    PROTECTED endpoint: Requires login.
    Returns sensitive user-specific data.
    """
    data = list(
        User.objects
        .annotate(friend_count=Count("friendships"))
        .values("user_id", "username", "friend_count")
        .order_by("user_id")
    )

    return JsonResponse(data, safe=False)