from activities.models import Friends
from django.shortcuts import get_object_or_404, render
from django.views import View
from django.views.generic import ListView

def friends_list(request):
    friends = Friends.objects.all()
    return render(request, "friend_list.html", {"friends": friends})
