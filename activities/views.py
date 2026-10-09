from django.db.models import Q
from django.db.models import Count
from django.http import HttpResponse
import requests
import csv
from datetime import datetime
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from django.contrib.auth.mixins import LoginRequiredMixin
from activities.models import Friends, Notifications, Recommendations, Activities
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.views.generic import ListView
from django.http import HttpResponse, JsonResponse
from django.template import loader


def home(request):
   return render(request, 'home.html')

@login_required
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

@login_required
def notifications(request):
   notification = Notifications.objects.all()
   template = loader.get_template("notifications.html")
   context = {"notifications": notifications}
   output = template.render(context, request)
   return HttpResponse(output)\
# view number 2 with HttpResponse


class Recommendation(LoginRequiredMixin, ListView):
    model = Recommendations
    template_name = "recommendations.html"
    context_object_name = "recommendations"


# api url
EXTERNAL_URL = "https://bored-api.appbrewery.com/filter"
# keys that work with the api
VALID_TYPES = {"education", "recreational", "social", "diy", "charity",
              "cooking", "relaxation", "music", "busywork"}




# the API's price is a relative score: 0 is free, higher is more expensive
@login_required

def price_label(p):
   if p is None:
       return "Unknown"
   if p == 0:
       return "Free"
   if p <= 0.2:
       return "$"
   if p <= 0.5:
       return "$$"
   return "$$$"



@login_required
def recommend_activity(request):
   q = request.GET.get("q", "")
   if not q:
       return JsonResponse({"error": "Missing query parameter ?q="}, status=400)
   if q not in VALID_TYPES:
       return JsonResponse({"error": f"Unknown type '{q}'",
                            "valid_types": sorted(VALID_TYPES)}, status=400)


   params = {"type": q}
   participants = request.GET.get("participants")
   if participants and participants.isdigit():
       params["participants"] = participants


   try:
       resp = requests.get(EXTERNAL_URL, params=params, timeout=5)
       if resp.status_code == 404:
           external = []  # no matches for this filter
       else:
           resp.raise_for_status()
           external = resp.json()
   except requests.Timeout:
       return JsonResponse({"error": "External API timed out"}, status=504)\
       # except api goes down


   except (requests.RequestException, ValueError):
       return JsonResponse({"error": "Could not fetch external data"}, status=502)
       # bad value


   if isinstance(external, dict):
       external = []




   internal_qs = Activities.objects.filter(category__iexact=q)
   internal_names = {a.activity_name.lower() for a in internal_qs}


   # create live
   suggestions = []
   for item in external[:15]:
       # change the external[:x] to adjust number of selection!!!!!!
       text = item.get("activity", "")
       suggestions.append({
           "activity": text,
           "type": item.get("type"),
           "participants": item.get("participants"),
           "price": item.get("price"),
           "cost": price_label(item.get("price")),
           "accessibility": item.get("accessibility"),
           "already_in_our_app": any(n in text.lower() or text.lower() in n
                                     for n in internal_names),
           # for each selection, extract this data
           # already in app crosscheck w/ our db.
       })


   # analytics
   prices = [s["price"] for s in suggestions if isinstance(s["price"], (int, float))]
   accessibility_counts = {}
   for s in suggestions:
       label = s["accessibility"] or "Unknown"
       accessibility_counts[label] = accessibility_counts.get(label, 0) + 1


   # apply analytics to data, give users an idea of how accesible the activity is.
   analytics = {
       "avg_price": round(sum(prices) / len(prices), 2) if prices else None,
           # average price of all the activities listed
       "free_count": sum(1 for s in suggestions if s["cost"] == "Free"),
           # count of free acitivites
       "accessibility_counts": accessibility_counts,
       "overlap_with_internal": sum(s["already_in_our_app"] for s in suggestions),
       "internal_category_counts": list(
           Activities.objects.values("category").annotate(total=Count("activity_id"))
       ),
   }
   # dictionary to return, handle jsonResponse in templates --> recommendations.html
   return JsonResponse({
       "query": q,
       "internal_matches": sorted(a.activity_name for a in internal_qs),
       "analytics": analytics,
       "suggestions": suggestions,
   })




# generic


class Hobbies(LoginRequiredMixin, View):


   def build_response(self, request, q):
       if q:
           activities = Activities.objects.filter(Q(activity_name__icontains=q))
       else:
           activities = Activities.objects.all()


       # Aggregations based on the filtered results
       total_activities = activities.count()
       activities_per_category = (
           activities
           .values('category')
           .annotate(total=Count('activity_id'))
           .order_by('-total')
       )


       return render(
           request,
           "activities.html",
           context={
               "Activities": activities,
               "q": q,
               "total_activities": total_activities,
               "totals": activities_per_category,
           }
       )


   def get(self, request):
       q = request.GET.get("q", "")
       return self.build_response(request, q)


   def post(self, request):
       q = request.POST.get("q") or request.GET.get("q") or ""
       return self.build_response(request, q)
# base
from django.views.generic import DetailView


class ActivityDetail(LoginRequiredMixin, DetailView):
   model = Activities
   template_name = "activity_detail.html"


class FriendDetail(LoginRequiredMixin, DetailView):
   model = Friends
   template_name = "friend_detail.html"


class NotificationDetail(LoginRequiredMixin, DetailView):
   model = Notifications
   template_name = "notifcation_detail.html"


import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from django.db.models import Count
import io

@login_required
def stats_chart(request):
   category_counts = Activities.objects.values('category').annotate(total=Count('activity_id')).order_by('-total')


   labels = [c['category'] or "Uncategorized" for c in category_counts]
   counts = [c['total'] for c in category_counts]


   fig, ax = plt.subplots()
   ax.bar(labels, counts, color='#4C72B0')
   ax.set_title('Activities per Category')
   ax.set_ylabel('Count')
   plt.xticks(rotation=30, ha='right')
   fig.tight_layout()


   buf = io.BytesIO()
   fig.savefig(buf, format='png')
   plt.close(fig)
   buf.seek(0)


   return HttpResponse(buf.getvalue(), content_type='image/png')



@login_required
def stats(request):
   return render(request, 'stats.html')

@login_required
def activities_csv(request):
   activities = Activities.objects.all().order_by("activity_name")


   timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")


   response = HttpResponse(content_type="text/csv")
   response["Content-Disposition"] = (
       f'attachment; filename="activities_{timestamp}.csv"'
   )


   writer = csv.writer(response)


   writer.writerow(["activity_id", "activity_name", "category"])


   for activity in activities:
       writer.writerow([
           activity.activity_id,
           activity.activity_name,
           activity.category,
       ])


   return response

@login_required
def activities_json(request):
   activities = Activities.objects.all().order_by("activity_name")


   data = {
       "generated_at": timezone.now().isoformat(),
       "record_count": activities.count(),
       "activities": [
           {
               "activity_id": activity.activity_id,
               "activity_name": activity.activity_name,
               "category": activity.category,
           }
           for activity in activities
       ],
   }


   timestamp = timezone.now().strftime("%Y-%m-%d_%H-%M")


   response = JsonResponse(
       data,
       json_dumps_params={"indent": 2}
   )


   response["Content-Disposition"] = (
       f'attachment; filename="activities_{timestamp}.json"'
   )


   return response

@login_required
def reports(request):
   activities = Activities.objects.all().order_by("activity_name")


   # Summary 1: activities grouped by category
   category_summary = (
       Activities.objects
       .values("category")
       .annotate(total=Count("activity_id"))
       .order_by("-total")
   )


   # Summary 2: activities grouped by activity name
   activity_summary = (
       Activities.objects
       .values("activity_name")
       .annotate(total=Count("activity_id"))
       .order_by("-total")
   )


   return render(
       request,
       "reports.html",
       {
           "activities": activities,
           "category_summary": category_summary,
           "activity_summary": activity_summary,
           "total_activities": activities.count(),
       },
   )



from django.contrib.auth import login
from .forms import CreateUser

def signup_view(request):
    """
    Show a sign-up form (GET),
    create an account (POST),
    then log the user in automatically.
    """
    if request.method == "POST":
        form = CreateUser(request.POST)
        if form.is_valid():
            # 1. Create the user in auth_user table
            new_user = form.save()

            # 2. Log them in immediately (no separate login step)
            login(request, new_user)

            # 3. Send them somewhere in the app
            return redirect("home")
    else:
        form = CreateUser()

    return render(request, "signup.html", {"form": form})



@login_required
def redirect_root_view(request):
    return redirect("notifications")



