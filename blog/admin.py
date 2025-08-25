from django.contrib import admin
from .models import BlogPost, Like, Subscriber

admin.site.register(BlogPost)
admin.site.register(Like)
admin.site.register(Subscriber)