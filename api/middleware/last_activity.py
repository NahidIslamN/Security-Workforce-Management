from django.utils import timezone
from api.models import Invoices

class UpdateLastActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated:
            request.user.last_activity = timezone.now()
            user = request.user
            last_invoice = Invoices.objects.filter(user=user).order_by('-created_at').first()
            if last_invoice:
                if last_invoice.end_date < timezone.now().date():
                    user.is_subscribe = False
                    user.save()
                    
                else:
                    pass
            else:
                user.is_subscribe = False
                user.save()
           

            request.user.save(update_fields=['last_activity'])
        return response
