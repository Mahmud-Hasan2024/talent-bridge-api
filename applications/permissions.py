from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsJobSeekerOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        user = request.user
        return user.is_authenticated and user.role == 'seeker'
