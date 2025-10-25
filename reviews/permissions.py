from rest_framework.permissions import BasePermission, SAFE_METHODS
from applications.models import Application

class CanReviewAcceptedJob(BasePermission):
    def has_permission(self, request, view):
        # Allow safe methods (GET, HEAD, OPTIONS)
        if request.method in SAFE_METHODS:
            return True

        user = request.user
        job_id = view.kwargs.get('job_pk')

        # Must be authenticated and a job seeker
        if not user.is_authenticated or user.role != 'seeker':
            return False

        # Must have an accepted application for that job
        return Application.objects.filter(
            job_id=job_id,
            applicant=user,
            status='accepted'
        ).exists()
