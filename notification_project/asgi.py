"""
ASGI config for notification_project project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notification_project.settings')

django_asgi_app = get_asgi_application()


import notifications.routing # Import your app's routing

application = ProtocolTypeRouter({
    "http": django_asgi_app, # Standard HTTP handling by Django
    "websocket": AllowedHostsOriginValidator( # WebSocket handling
        AuthMiddlewareStack( # Ensures user is authenticated for WebSocket
            URLRouter(
                notifications.routing.websocket_urlpatterns # Your WebSocket routes
            )
        )
    ),
})