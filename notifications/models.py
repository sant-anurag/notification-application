# notifications/models.py
from django.db import models
from django.contrib.auth.models import User
from blog.models import BlogPost # Import BlogPost model

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('new_post', 'New Blog Post'),
        ('post_liked', 'Blog Post Liked'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    related_post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at'] # Order by newest first

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"