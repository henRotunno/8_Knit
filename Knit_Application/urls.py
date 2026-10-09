"""
URL configuration for Knit_Application project.


The `urlpatterns` list routes URLs to views. For more information please see:
   https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
   1. Add an import:  from my_app import views
   2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
   1. Add an import:  from other_app.views import Home
   2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
   1. Import the include() function: from django.urls import include, path
   2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


from django.contrib import admin
from django.urls import path, include
from activities import views
from activities.api_views import (
   activities_api,
   activities_http_api,
   activity_category_summary,
   user_friend_summary
)
from django.views.generic import TemplateView
from django.views.generic import RedirectView
from django.templatetags.static import static
from django.contrib.auth.views import LoginView, LogoutView






urlpatterns = [
   path("admin/", admin.site.urls),
   path("friends/", views.friends_list, name="friends"),
   path("notifications/", views.notifications, name="notifications"),
   path("recommendations/", views.Recommendation.as_view(), name="recommendations"),
   path("activities/", views.Hobbies.as_view(), name="activities"),
   path("", views.home, name="home"),
   path("activities/<int:pk>/", views.ActivityDetail.as_view(), name="activity-detail"),
   path("friends/<int:pk>/", views.FriendDetail.as_view(), name="friend-detail"),
   path("notifications/<int:pk>/", views.NotificationDetail.as_view(), name="notification-detail"),
   path("reports/", views.reports, name="reports"),
   path("api/activities/", activities_api, name="activities_api"),
   path("api/activities-http/", activities_http_api, name="activities_http_api"),
   path("stats-chart/", views.stats_chart, name="stats-chart"),
   path("stats/", views.stats, name="stats"),
   path("api/recommend/", views.recommend_activity, name="recommend_activity"),
   path(
        "api/chart/activity-categories/",
        activity_category_summary,
        name="activity_category_summary",
       ),
   path(
        "api/chart/user-friends/",
        user_friend_summary,
        name="user_friend_summary",
       ),
   path(
       "vega-lite/",
       TemplateView.as_view(template_name="vega_charts.html"),
       name="vega-charts",
       ),
   path(
       "vega-lite/chart1.png",
       RedirectView.as_view(
           url=static("vega/activity_categories_bar.png"),
           permanent=False,
       ),
       name="vega-chart1",
   ),


   path(
       "vega-lite/chart2.png",
       RedirectView.as_view(
           url=static("vega/user_friends_scatter.png"),
           permanent=False,
       ),
       name="vega-chart2",
   ),
   path(
       "exports/activities/csv/",
       views.activities_csv,
       name="activities_csv",
   ),


   path(
       "exports/activities/json/",
       views.activities_json,
       name="activities_json",
   ),


    path('login/',
         LoginView.as_view(template_name='login.html'),
         name='login_urlpattern'),


    path('logout/',
         LogoutView.as_view(),
         name='logout_urlpattern'),

    path("signup/", views.signup_view, name="signup_urlpattern"),

    path('accounts/', include('allauth.urls')),
]



