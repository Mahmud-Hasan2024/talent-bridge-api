from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrEmployer(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        return user.is_authenticated and user.role in ['admin', 'employer']


class IsAdminOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        return user.is_authenticated and user.role == 'admin'
