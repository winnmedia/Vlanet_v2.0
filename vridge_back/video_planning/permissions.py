from rest_framework.permissions import BasePermission

class AllowAnyTemporary(BasePermission):
    """   -   """
    def has_permission(self, request, view):
        return True