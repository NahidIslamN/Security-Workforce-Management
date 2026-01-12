
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from managements.views import SubscribeNow
from api.views import GetMyPolan
from managements.hock import stripe_webhook

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('api.urls')),
    path('api/chat-note/', include('chat_app.urls')),
    path('api/accounts/', include('user_profile.urls')),
    path('api/jobs/', include('managements.urls')),
    path('api/admin/', include('admin_deshboard.urls')),
    path('api/subscribe/<int:plan_id>/', SubscribeNow.as_view()),
    path('api/subscribe/pay-success/', stripe_webhook, name="pay-success"),
    path('api/get-plans/', GetMyPolan.as_view(), name="get-plans"),
    

]


if settings.DEBUG:
       
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)