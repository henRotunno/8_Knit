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
from django.urls import path
from activities import views



urlpatterns = [
    path("admin/", admin.site.urls),
    path("friends/", views.friends_list, name="friends"),
    path("notifications/", views.notifications, name="notifications"),
    path("recommendations/", views.Recommendation.as_view(), name="recommendations"),
    path("activities/", views.Hobbies.as_view(), name="activities"),]
