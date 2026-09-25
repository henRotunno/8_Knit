from activities.models import Friends, Notifications, Recommendations, Activities
from django.shortcuts import get_object_or_404, render
from django.views import View
from django.views.generic import ListView
from django.http import HttpResponse
from django.template import loader

def home(request):
    return render(request, 'home.html')

def friends_list(request):
    friends = Friends.objects.all()
    return render(request, "friend_list.html", {"friends": friends})
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
        return render(
            request,
            'activities.html',
            context={'Activities': Activities.objects.all()}
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

