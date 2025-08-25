# blog/models.py
from django.db import models
from django.contrib.auth.models import User

class BlogPost(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    blog_post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'blog_post') # A user can only like a post once

    def __str__(self):
        return f"{self.user.username} likes {self.blog_post.title}"

class Subscriber(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    # In a real app, you might have a 'blog' foreign key here if users subscribe to specific blogs
    # For this POC, let's assume 'subscribing' means receiving all new blog post notifications.

    def __str__(self):
        return f"{self.user.username} is a subscriber"