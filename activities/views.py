from django.db.models import Q

from activities.models import Friends, Notifications, Recommendations, Activities
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.views.generic import ListView
from django.http import HttpResponse
from django.template import loader

def home(request):
    return render(request, 'home.html')

def friends_list(request):
    friends = Friends.objects.all()
    q = ""


    if request.method == "POST":
        q = request.POST.get("q", "")

        if q:
            friends = Friends.objects.filter(Q(friend__username__icontains=q))
    return render(
    request,
    'friend_list.html',
    context={'Friends': friends, 'q': q, 'count': Friends.objects.count()}
    )
# view number 1 with render

def notifications(request):
    notification = Notifications.objects.all()
    template = loader.get_template("notifications.html")
    context = {"notifications": notifications}
    output = template.render(context, request)
    return HttpResponse(output)\
# view number 2 with HttpResponse


class Recommendation(ListView):
    model = Recommendations
    template_name = "recommendations.html"
    context_object_name = "recommendations"
# generic

class Hobbies(View):

    def get(self, request):
        q = request.GET.get("q", "")

        if q:
            activities = Activities.objects.filter(
                Q(activity_name__icontains=q)
            )
        else:
            activities = Activities.objects.all()

        return render(
            request,
            "activities.html",
            context={
                "Activities": activities,
                "q": q
            }
        )

    def post(self, request):
        q = request.POST.get("q") or request.GET.get("q")

        if q:
            activities = Activities.objects.filter(
                Q(activity_name__icontains=q)
            )
        else:
            activities = Activities.objects.all()

        return render(
            request,
            "activities.html",
            context={
                "Activities": activities,
                "q": q
            }
        )
# base
from django.views.generic import DetailView

class ActivityDetail(DetailView):
    model = Activities
    template_name = "activity_detail.html"

class FriendDetail(DetailView):
    model = Friends
    template_name = "friend_detail.html"

class NotificationDetail(DetailView):
    model = Notifications
    template_name = "notifcation_detail.html"

