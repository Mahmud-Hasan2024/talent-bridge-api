from jobs.models import Job, JobCategory
from jobs.serializers import JobSerializer, JobCategorySerializer
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from jobs.filters import JobFilter
from rest_framework.filters import SearchFilter, OrderingFilter
from jobs.paginations import DefaultPagination
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from jobs.permissions import IsAdminOrEmployer, IsAdminOnly
from drf_yasg.utils import swagger_auto_schema

# Create your views here.

class JobViewSet(ModelViewSet):
    queryset = Job.objects.select_related("category").all().order_by("-created_at")
    serializer_class = JobSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = JobFilter
    search_fields = ["title", "company_name", "description", "location"]
    ordering_fields = ["created_at", "company_name", "title"]
    pagination_class = DefaultPagination

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticatedOrReadOnly()]
        return [IsAuthenticated(), IsAdminOrEmployer()]

    @swagger_auto_schema(
        operation_summary="List jobs",
        operation_description="Returns a paginated list of jobs. Supports filter, search and ordering."
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve job",
        operation_description="Get job detail by id"
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class JobCategoryViewSet(ModelViewSet):
    queryset = JobCategory.objects.annotate(job_count=Count("jobs")).all()
    serializer_class = JobCategorySerializer
    pagination_class = None

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticatedOrReadOnly()]
        return [IsAuthenticated(), IsAdminOrEmployer()]

    @swagger_auto_schema(operation_summary="List job categories")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
