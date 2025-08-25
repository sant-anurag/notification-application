# notifications/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from blog.models import BlogPost, Like, Subscriber
from .models import Notification

@receiver(post_save, sender=BlogPost)
def create_new_post_notification(sender, instance, created, **kwargs):
    if created:
        # Create a notification for all subscribers
        subscribers = Subscriber.objects.all()
        for subscriber in subscribers:
            # Create the notification object in the database
            notification = Notification.objects.create(
                user=subscriber.user,
                message=f'A new blog post titled "{instance.title}" has been published!',
                notification_type='new_post',
                related_post=instance
            )
            # Push the notification to the user's channel group
            channel_layer = get_channel_layer()
            group_name = f'user_notifications_{subscriber.user.id}'
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    'type': 'send_notification',
                    'message': notification.message,
                    'notification_type': notification.notification_type,
                    'notification_id': notification.id,
                    'is_read': notification.is_read
                }
            )

@receiver(post_save, sender=Like)
def create_like_notification(sender, instance, created, **kwargs):
    if created:
        # Get the author of the liked post
        author = instance.blog_post.author
        # Create the notification object in the database
        notification = Notification.objects.create(
            user=author,
            message=f'Your post "{instance.blog_post.title}" was liked by {instance.user.username}!',
            notification_type='post_liked',
            related_post=instance.blog_post
        )
        # Push the notification to the author's channel group
        channel_layer = get_channel_layer()
        group_name = f'user_notifications_{author.id}'
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'send_notification',
                'message': notification.message,
                'notification_type': notification.notification_type,
                'notification_id': notification.id,
                'is_read': notification.is_read
            }
        )