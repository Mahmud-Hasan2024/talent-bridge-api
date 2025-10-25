from django.forms import ValidationError
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from applications.models import Application
from applications.serializers import ApplicationSerializer
from applications.permissions import IsJobSeekerOrReadOnly
from jobs.models import Job
from drf_yasg.utils import swagger_auto_schema

# Create your views here.

class ApplicationViewSet(ModelViewSet):
    """
    ViewSet for applications.
    - Job seekers see only their own applications.
    - Employers see applications to their own jobs.
    - Admins see everything.
    """
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated, IsJobSeekerOrReadOnly]

    def get_queryset(self):
        # Avoid executing logic during drf_yasg schema generation
        if getattr(self, "swagger_fake_view", False):
            return Application.objects.none()

        user = self.request.user
        # Safety: if anonymous return empty queryset
        if not user.is_authenticated:
            return Application.objects.none()

        # Job seekers see only their own applications
        if getattr(user, "role", None) == "seeker":
            return Application.objects.filter(applicant=user)

        # Employers see applications to their own jobs
        if getattr(user, "role", None) == "employer":
            return Application.objects.filter(job__employer=user)

        # Admin sees everything
        if getattr(user, "role", None) == "admin":
            return Application.objects.all()

        return Application.objects.none()

    @swagger_auto_schema(
        operation_summary="Create application for a job",
        operation_description="Job seekers can apply to a job. `job_pk` is expected from the nested route.",
        responses={201: ApplicationSerializer()}
    )
    def perform_create(self, serializer):
        # In normal usage job_pk should come from nested URL
        job_id = self.kwargs.get("job_pk")
        user = self.request.user

        if not user.is_authenticated or getattr(user, "role", None) != "seeker":
            raise PermissionDenied("Only job seekers can apply for jobs.")

        if not job_id:
            raise ValidationError("Missing job id in URL.")

        # Prevent applying twice for the same job
        if Application.objects.filter(job_id=job_id, applicant=user).exists():
            raise ValidationError("You have already applied for this job.")

        job = Job.objects.get(id=job_id)
        serializer.save(job=job, applicant=user)

    @swagger_auto_schema(operation_summary="Update an application (status)")
    def perform_update(self, serializer):
        user = self.request.user
        application = self.get_object()

        if getattr(user, "role", None) == "employer" and application.job.employer != user:
            raise PermissionDenied("You can only update applications for your own jobs.")
        elif getattr(user, "role", None) not in ["employer", "admin"]:
            raise PermissionDenied("Only employers or admins can update application status.")
        serializer.save()

    @swagger_auto_schema(
        operation_summary="Withdraw an application",
        operation_description="Job seeker withdraws their own application (if allowed)."
    )
    @action(detail=True, methods=["post"])
    def withdraw(self, request, pk=None, job_pk=None):
        user = request.user
        application = self.get_object()

        if not user.is_authenticated or getattr(user, "role", None) != "seeker" or application.applicant != user:
            return Response({"detail": "You can only withdraw your own applications."}, status=403)

        if application.status in ["accepted", "rejected", "withdrawn"]:
            return Response({"detail": f"Cannot withdraw application with status '{application.status}'."}, status=400)

        application.status = "withdrawn"
        application.save()
        return Response({"detail": "Application successfully withdrawn."})
