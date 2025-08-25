from django.contrib import admin

from .models import Notification

# Register your models here.
admin.site.site_header = "Notification Admin"
admin.site.register(Notification)