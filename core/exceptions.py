from rest_framework.views import exception_handler

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    # Token invalid → AuthenticationFailed or NotAuthenticated
    if response is not None:
        if response.status_code == 401:
            response.data = {
                "status": False,
                "message": "Invalid or expired token"
            }
            
    return response
