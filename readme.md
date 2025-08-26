## Building a Real-Time In-App Notification System with Django and WebSockets

In today's dynamic web landscape, real-time updates and notifications are crucial for engaging users and providing a seamless experience. In this article, we'll walk through the process of building a robust and efficient real-time in-app notification system using the power of Django and WebSockets, specifically leveraging Django Channels and Redis.

This guide is designed to help fellow developers understand the core concepts and implement a proof-of-concept (POC) application. We'll consider a common scenario: a blog application where subscribers are notified of new posts and authors receive alerts when their content is liked.

### Prerequisites

  * Basic understanding of Django framework.
  * Python 3.x installed.
  * pip installed.
  * Redis server installed and running locally (or accessible).

### Setting Up the Foundation

Let's start by creating a Django project and a core application for our notifications.

1.  **Create a Django Project:**

    In your terminal, run:

    \`\`\`bash
    django-admin startproject django\_notifications
    cd django\_notifications
    python manage.py startapp notifications
    python manage.py startapp blog
    \`\`\`

2.  **Install Dependencies:**

    We need `channels` and `channels_redis` for WebSocket support and Redis integration.

    \`\`\`bash
    pip install channels channels\_redis daphne
    \`\`\`

    *Note: We're including `daphne` explicitly here. While Django Channels often manages its use, explicitly adding it to our dependencies and potentially `INSTALLED_APPS` can resolve some environment-specific issues related to the ASGI server.*

3.  **Configure `settings.py`:**

    Open your project's `settings.py` and make the following changes:

      * Add `'channels'`, `'notifications'`, and `'blog'` to `INSTALLED_APPS`:

        \`\`\`python
        INSTALLED\_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'channels',
        'notifications',
        'blog',
        ]
        \`\`\`

      * Configure the ASGI application and Channels' channel layer to use Redis:

        \`\`\`python
        ASGI\_APPLICATION = 'django\_notifications.asgi.application'

        CHANNEL\_LAYERS = {
        'default': {
        'BACKEND': 'channels\_redis.pubsub.RedisPubSubChannelLayer',
        'CONFIG': {
        "hosts": [('127.0.0.1', 6379)],
        },
        },
        }
        \`\`\`

      * Configure static files:

        \`\`\`python
        STATIC\_URL = '/static/'
        STATICFILES\_DIRS = [
        BASE\_DIR / 'static',
        ]
        \`\`\`

### Defining Our Models

We need models to represent our blog posts, likes, and the notifications themselves.

1.  **`blog/models.py`:**

    \`\`\`python
    from django.db import models
    from django.contrib.auth.models import User

    class BlogPost(models.Model):
    author = models.ForeignKey(User, on\_delete=models.CASCADE, related\_name='blog\_posts')
    title = models.CharField(max\_length=200)
    content = models.TextField()
    created\_at = models.DateTimeField(auto\_now\_add=True)
    updated\_at = models.DateTimeField(auto\_now=True)

    ```
    def \_\_str\_\_(self):
        return self.title
    ```

    class Like(models.Model):
    user = models.ForeignKey(User, on\_delete=models.CASCADE, related\_name='likes')
    blog\_post = models.ForeignKey(BlogPost, on\_delete=models.CASCADE, related\_name='likes')
    created\_at = models.DateTimeField(auto\_now\_add=True)

    ```
    class Meta:
        unique\_together = ('user', 'blog\_post')

    def \_\_str\_\_(self):
        return f"{self.user.username} likes {self.blog\_post.title}"
    ```

    class Subscriber(models.Model):
    user = models.ForeignKey(User, on\_delete=models.CASCADE, related\_name='subscriptions')

    ```
    def \_\_str\_\_(self):
        return f"{self.user.username} is a subscriber"
    ```

    \`\`\`

2.  **`notifications/models.py`:**

    \`\`\`python
    from django.db import models
    from django.contrib.auth.models import User
    from blog.models import BlogPost

    class Notification(models.Model):
    NOTIFICATION\_TYPES = (
    ('new\_post', 'New Blog Post'),
    ('post\_liked', 'Blog Post Liked'),
    )

    ```
    user = models.ForeignKey(User, on\_delete=models.CASCADE, related\_name='notifications')
    message = models.TextField()
    notification\_type = models.CharField(max\_length=20, choices=NOTIFICATION\_TYPES)
    related\_post = models.ForeignKey(BlogPost, on\_delete=models.CASCADE, null=True, blank=True)
    is\_read = models.BooleanField(default=False)
    created\_at = models.DateTimeField(auto\_now\_add=True)

    class Meta:
        ordering = ['-created\_at']

    def \_\_str\_\_(self):
        return f"Notification for {self.user.username}: {self.message}"
    ```

    \`\`\`

3.  **Make Migrations:**

    \`\`\`bash
    python manage.py makemigrations
    python manage.py migrate
    \`\`\`

### Configuring ASGI and Routing

Django Channels uses ASGI instead of WSGI. We need to configure our project's `asgi.py` and create a routing file for our notifications app.

1.  **`django_notifications/asgi.py`:**

    \`\`\`python
    import os

    from channels.auth import AuthMiddlewareStack
    from channels.routing import ProtocolTypeRouter, URLRouter
    from django.core.asgi import get\_asgi\_application
    from channels.security.websocket import AllowedHostsOriginValidator

    os.environ.setdefault('DJANGO\_SETTINGS\_MODULE', 'django\_notifications.settings')

    django\_asgi\_app = get\_asgi\_application()

    import notifications.routing

    application = ProtocolTypeRouter({
    "http": django\_asgi\_app,
    "websocket": AllowedHostsOriginValidator(
    AuthMiddlewareStack(
    URLRouter(
    notifications.routing.websocket\_urlpatterns
    )
    )
    ),
    })
    \`\`\`

2.  **`notifications/routing.py`:**

    \`\`\`python
    from django.urls import re\_path
    from . import consumers

    websocket\_urlpatterns = [
    re\_path(r'ws/notifications/$', consumers.NotificationConsumer.as\_asgi()),
    ]
    \`\`\`

### Building the Notification Consumer

The consumer handles WebSocket connections and sends messages.

1.  **`notifications/consumers.py`:**

    \`\`\`python
    import json
    from channels.generic.websocket import AsyncWebsocketConsumer
    from asgiref.sync import sync\_to\_async

    class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
    self.user = self.scope["user"]
    if self.user.is\_authenticated:
    self.group\_name = f'user\_notifications\_{self.user.id}'
    await self.channel\_layer.group\_add(
    self.group\_name,
    self.channel\_name
    )
    await self.accept()
    print(f"WebSocket connected for user: {self.user.username}")
    else:
    await self.close()
    print("WebSocket connection rejected: User not authenticated")

    ```
    async def disconnect(self, close\_code):
        if self.user.is\_authenticated:
            await self.channel\_layer.group\_discard(
                self.group\_name,
                self.channel\_name
            )
            print(f"WebSocket disconnected for user: {self.user.username}")

    async def receive(self, text\_data):
        pass

    async def send\_notification(self, event):
        message = event['message']
        notification\_type = event['notification\_type']
        notification\_id = event['notification\_id']
        is\_read = event['is\_read']

        await self.send(text\_data=json.dumps({
            'message': message,
            'notification\_type': notification\_type,
            'notification\_id': notification\_id,
            'is\_read': is\_read,
        }))
        print(f"Sent notification to {self.user.username}: {message}")
    ```

    \`\`\`

### Triggering Notifications with Signals

Django signals allow us to execute code automatically when certain events occur. We'll use `post_save` signals to create notifications.

1.  **`notifications/signals.py`:**

    \`\`\`python
    from django.db.models.signals import post\_save
    from django.dispatch import receiver
    from asgiref.sync import async\_to\_sync
    from channels.layers import get\_channel\_layer
    from blog.models import BlogPost, Like, Subscriber
    from .models import Notification

    @receiver(post\_save, sender=BlogPost)
    def create\_new\_post\_notification(sender, instance, created, \*\*kwargs):
    if created:
    subscribers = Subscriber.objects.all()
    for subscriber in subscribers:
    notification = Notification.objects.create(
    user=subscriber.user,
    message=f'A new blog post titled "{instance.title}" has been published\!',
    notification\_type='new\_post',
    related\_post=instance
    )
    channel\_layer = get\_channel\_layer()
    group\_name = f'user\_notifications\_{subscriber.user.id}'
    async\_to\_sync(channel\_layer.group\_send)(
    group\_name,
    {
    'type': 'send\_notification',
    'message': notification.message,
    'notification\_type': notification.notification\_type,
    'notification\_id': notification.id,
    'is\_read': notification.is\_read
    }
    )

    @receiver(post\_save, sender=Like)
    def create\_like\_notification(sender, instance, created, \*\*kwargs):
    if created:
    author = instance.blog\_post.author
    notification = Notification.objects.create(
    user=author,
    message=f'Your post "{instance.blog\_post.title}" was liked by {instance.user.username}\!',
    notification\_type='post\_liked',
    related\_post=instance.blog\_post
    )
    channel\_layer = get\_channel\_layer()
    group\_name = f'user\_notifications\_{author.id}'
    async\_to\_sync(channel\_layer.group\_send)(
    group\_name,
    {
    'type': 'send\_notification',
    'message': notification.message,
    'notification\_type': notification.notification\_type,
    'notification\_id': notification.id,
    'is\_read': notification.is\_read
    }
    )
    \`\`\`

2.  **Register Signals in `notifications/apps.py`:**

    \`\`\`python
    from django.apps import AppConfig

    class NotificationsConfig(AppConfig):
    default\_auto\_field = 'django.db.models.BigAutoField'
    name = 'notifications'

    ```
    def ready(self):
        import notifications.signals
    ```

    \`\`\`

### Frontend Implementation

Finally, we need to connect to the WebSocket from our frontend using JavaScript.

1.  **Create `static/js/notifications.js`:**

    \`\`\`javascript
    document.addEventListener('DOMContentLoaded', function() {
    const notificationBadge = document.getElementById('notification-badge');

    ```
    function updateBadgeCount(count) {
        if (count > 0) {
            notificationBadge.innerText = count;
            notificationBadge.style.display = 'inline';
        } else {
            notificationBadge.style.display = 'none';
        }
    }

    fetch('/notifications/count/')
        .then(response => response.json())
        .then(data => {
            updateBadgeCount(data.count);
        });

    const socket = new WebSocket('ws://' + window.location.host + '/ws/notifications/');

    socket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        console.log('Received real-time notification:', data);

        const currentCount = parseInt(notificationBadge.innerText) || 0;
        updateBadgeCount(currentCount + 1);

        alert(data.message); // For POC, show an alert
    };

    socket.onclose = function(e) {
        console.log('WebSocket closed unexpectedly');
    };
    ```

    });
    \`\`\`

2.  **Include JavaScript in your base template (`templates/base.html`):**

    Ensure you have a base template and include the following before the closing `</body>` tag:

    \`\`\`html

    \<script src="[https://code.jquery.com/jquery-3.6.0.min.js](https://www.google.com/search?q=https://code.jquery.com/jquery-3.6.0.min.js)"\>\</script\>

    {% if user.is\_authenticated %}
    \<script\>
    const userId = {{ user.id }};
    \</script\>
    {% load static %}
    \<script src="{% static 'js/notifications.js' %}"\>\</script\>
    {% endif %}
    \`\`\`

    Also, add a placeholder for the notification icon and badge in your navigation:

    \`\`\`html
    \<span class="notification-icon"\>
    🔔
    \<span id="notification-badge" class="notification-badge"\>0\</span\>
    \</span\>
    \`\`\`

### Running the Application

1.  **Start Redis Server:**

    Open a new terminal and run `redis-server`.

2.  **Start Django Development Server:**

    In your project terminal, run `python manage.py runserver`.

Now, when you create a new blog post (as a non-subscriber user) and a subscriber is logged in, the subscriber should receive a real-time notification. Similarly, when a subscriber likes a post, the author should receive a notification instantly.

### Conclusion

This walkthrough demonstrates the fundamental steps in building a real-time in-app notification system using Django Channels and WebSockets. By leveraging the asynchronous capabilities of Channels and the efficient messaging of Redis, you can create engaging and responsive applications that provide immediate updates to your users.

This POC can be further extended by adding features like marking notifications as read, displaying notifications in a dedicated UI element, different notification types, and more sophisticated frontend handling. The power of Django Channels opens up a world of possibilities for building interactive and real-time web applications.

Remember to consider error handling, scalability, and security when implementing such systems in production environments. Happy coding\!