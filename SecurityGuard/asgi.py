import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SecurityGuard.settings")

# Initialize Django BEFORE importing anything that uses models
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

# Import these AFTER django.setup()
from SecurityGuard.custom_auth import CustomAuthMiddleware
from chat_app.routing import websocket_urlpatterns

application = ProtocolTypeRouter(
    {
        'http': get_asgi_application(),
        "websocket": AllowedHostsOriginValidator(
            CustomAuthMiddleware(
                URLRouter(
                    websocket_urlpatterns
                )
            )
        )
    }
)