"""
ASGI config for notification_project project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import notifications.routing # Import your app's routing
# from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notification_project.settings')




application = ProtocolTypeRouter({
    "http": get_asgi_application(), # Standard HTTP handling by Django
    "websocket": # AllowedHostsOriginValidator( # WebSocket handling
        AuthMiddlewareStack( # Ensures user is authenticated for WebSocket
            URLRouter(
                notifications.routing.websocket_urlpatterns # Your WebSocket routes
            )
        )
    # ),
})