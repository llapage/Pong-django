import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mainApp.settings")

# Initialize Django ASGI application
django_asgi_app = get_asgi_application()

# Import WebSocket URL patterns from multiple apps
from chatApp.routing import websocket_urlpatterns as chat_patterns
from matchmakingApp.routing import websocket_urlpatterns as matchmaking_patterns

websocket_urlpatterns = chat_patterns + matchmaking_patterns

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
        ),
    }
)
