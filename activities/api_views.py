import json

from django.http import JsonResponse, HttpResponse
from activities.models import Activities


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