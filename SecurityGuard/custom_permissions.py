from rest_framework import permissions

class IsCompany(permissions.BasePermission):
    def has_permission(self, request, view):
        # Check if user is authenticated and is staff
        return bool(request.user and request.user.is_authenticated and request.user.is_email_varified and request.user.user_type == "company")


class IsSubscribe(permissions.BasePermission):
    def has_permission(self, request, view):
        # Check if user is authenticated and is staff
        return bool(request.user and request.user.is_authenticated) #and request.user.is_subscribe



class IsEmailVerified(permissions.BasePermission):
    def has_permission(self, request, view):
        
        
        return bool(request.user and request.user.is_authenticated and request.user.is_email_varified)
    


class IsGuard(permissions.BasePermission):
    def has_permission(self, request, view):
        
        
        return bool(request.user and request.user.is_authenticated and request.user.is_email_varified and request.user.user_type == 'guard' and request.user.is_admin_aproved)



class IsGuard(permissions.BasePermission):
    def has_permission(self, request, view):
        
        
        return bool(request.user and request.user.is_authenticated and request.user.is_email_varified and request.user.user_type == 'guard')


class Is_Admin_Verified(permissions.BasePermission):
    def has_permission(self, request, view):

        return request.user.is_admin_aproved

