from django.db import models
from django.urls import reverse

# Create your models here.
"""""
Standard table for all users, required username, email, password.

Auto assigns user_id, primary key
"""""
# ---Parent table---
class User(models.Model):
    user_id = models.AutoField(primary_key=True) # Primary key
    username = models.CharField(max_length=14)
    email = models.EmailField(max_length=50, unique=True)
    password = models.CharField(max_length=16)



""""
Table for all of the UNIQUE activities 
Sorted by activity_name
"""""

class Activities(models.Model):
    activity_id = models.AutoField(primary_key=True) # one to many from User table
    activity_name = models.CharField(max_length=40, unique=True) # constraint, avoid duplicate activities


    class Meta:
        ordering = ['activity_name']

    def __str__(self):
        return self.activity_name

    def get_absolute_url(self):
        return reverse("activity-detail", kwargs={"pk": self.pk})
""""
Table for notifications, describes what the notification is, the time, and if the message was read
"""""
class Notifications(models.Model):
    notification_id = models.AutoField(primary_key=True) # primary key
    user_id = models.ForeignKey(User, on_delete=models.CASCADE) # Foreign key
    notification_message = models.TextField()
    time = models.DateTimeField(auto_now_add=True)
    read_message = models.BooleanField(default=False) # 1 or 0
""""
Table for recent activies, includes the approx location, group size, activity name, and time.
"""""
class RecentActivities(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_id = models.ForeignKey(Activities, on_delete=models.CASCADE)
    activity_name = models.CharField(max_length=40)
    time = models.DateTimeField(auto_now_add=True)
    approx_location = models.CharField(max_length=40, null=True, blank=True)
    group_size = models.IntegerField(null=True,blank=True)

""""
Table for all of the recommendation feature  
Includes the recommended activities.
"""""
class Recommendations(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_id = models.ForeignKey(Activities, on_delete=models.CASCADE)
    recommendation_name = models.CharField(max_length=40)

# render view (function based 1)
class Friends(models.Model):
    friendslist_id = models.AutoField(primary_key=True)  # primary key
    user_id = models.ForeignKey(User, on_delete=models.CASCADE) # user


# http response (function based 2)


















