from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Activities
from .models import RecentActivities
from .models import Recommendations
from .models import Notifications
from .models import User

admin.site.register(Activities)
admin.site.register(RecentActivities)
admin.site.register(Recommendations)
admin.site.register(Notifications)
admin.site.register(User)
