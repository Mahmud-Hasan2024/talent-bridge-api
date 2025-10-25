# JobBoardAPI - Project scaffold
# This single file contains project structure and starter code snippets you can copy into
# your Django project files. Files are marked with a header like: ### FILE: <path>

##############################
### PROJECT TREE
##############################
# jobboard/
# ├── jobboard/
# │   ├── __init__.py
# │   ├── settings.py
# │   ├── urls.py
# │   └── wsgi.py
# ├── accounts/
# │   ├── __init__.py
# │   ├── models.py
# │   ├── serializers.py
# │   ├── views.py
# │   ├── urls.py
# │   └── signals.py
# ├── jobs/
# │   ├── __init__.py
# │   ├── models.py
# │   ├── serializers.py
# │   ├── views.py
# │   └── urls.py
# ├── applications/
# │   ├── __init__.py
# │   ├── models.py
# │   ├── serializers.py
# │   ├── views.py
# │   └── urls.py
# ├── reviews/
# │   ├── __init__.py
# │   ├── models.py
# │   ├── serializers.py
# │   ├── views.py
# │   └── urls.py
# ├── notifications/ (optional)
# ├── media/
# └── manage.py


##############################
### FILE: jobboard/settings.py (partial - add to your settings)
##############################

INSTALLED_APPS = [
    # Django defaults ...
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',

    # Local apps
    'accounts',
    'jobs',
    'applications',
    'reviews',
    'notifications',
]

AUTH_USER_MODEL = 'accounts.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
}

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# Configure SMTP settings in env vars for production

##############################
### FILE: jobboard/urls.py
##############################

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    path('api/jobs/', include('jobs.urls')),
    path('api/applications/', include('applications.urls')),
    path('api/reviews/', include('reviews.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

##############################
### FILE: accounts/models.py
##############################

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_ADMIN = 'admin'
    ROLE_EMPLOYER = 'employer'
    ROLE_SEEKER = 'seeker'

    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Admin'),
        (ROLE_EMPLOYER, 'Employer'),
        (ROLE_SEEKER, 'Job Seeker'),
    ]

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_SEEKER)
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.email} ({self.role})"

##############################
### FILE: accounts/serializers.py
##############################

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
from django.urls import reverse
from django.core.mail import send_mail

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'role')

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.is_active = True  # allow creation; block login until verified
        user.is_verified = False
        user.save()
        # Send verification email
        self.send_verification_email(user)
        return user

    def send_verification_email(self, user):
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        verify_path = reverse('accounts:verify-email', kwargs={'uidb64': uid, 'token': token})
        verify_url = f"{settings.FRONTEND_BASE_URL}{verify_path}"
        subject = 'Verify your email'
        message = f"Click the link to verify your account: {verify_url}"
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'role', 'is_verified')

##############################
### FILE: accounts/views.py
##############################

from rest_framework import generics, status, permissions
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, UserSerializer
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class VerifyEmailView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except Exception:
            return Response({'detail': 'Invalid link'}, status=status.HTTP_400_BAD_REQUEST)

        if default_token_generator.check_token(user, token):
            user.is_verified = True
            user.save()
            return Response({'detail': 'Email verified'}, status=status.HTTP_200_OK)
        return Response({'detail': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

##############################
### FILE: accounts/urls.py
##############################

from django.urls import path
from .views import RegisterView, VerifyEmailView, ProfileView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

app_name = 'accounts'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('verify-email/<uidb64>/<token>/', VerifyEmailView.as_view(), name='verify-email'),
    path('profile/', ProfileView.as_view(), name='profile'),
]

##############################
### FILE: accounts/signals.py (hook to add default group)
##############################

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()

@receiver(post_save, sender=User)
def assign_default_group(sender, instance, created, **kwargs):
    if created:
        if instance.role == User.ROLE_EMPLOYER:
            group, _ = Group.objects.get_or_create(name='Employer')
            instance.groups.add(group)
        elif instance.role == User.ROLE_SEEKER:
            group, _ = Group.objects.get_or_create(name='Subscriber')
            instance.groups.add(group)
        elif instance.role == User.ROLE_ADMIN:
            group, _ = Group.objects.get_or_create(name='Admin')
            instance.groups.add(group)
        instance.save()

##############################
### FILE: jobs/models.py
##############################

from django.db import models
from django.conf import settings

class JobCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Job(models.Model):
    employer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    description = models.TextField()
    requirements = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    category = models.ForeignKey(JobCategory, on_delete=models.SET_NULL, null=True, related_name='jobs')
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} at {self.company_name}"

##############################
### FILE: jobs/serializers.py
##############################

from rest_framework import serializers
from .models import Job, JobCategory

class JobCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = JobCategory
        fields = ('id', 'name')

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ('id', 'employer', 'title', 'company_name', 'description', 'requirements', 'location', 'category', 'is_featured', 'created_at')
        read_only_fields = ('employer', 'created_at')

class JobDetailSerializer(JobSerializer):
    category = JobCategorySerializer()

##############################
### FILE: jobs/views.py
##############################

from rest_framework import viewsets, permissions
from .models import Job, JobCategory
from .serializers import JobSerializer, JobCategorySerializer

class IsEmployer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == request.user.ROLE_EMPLOYER

class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all().order_by('-created_at')
    serializer_class = JobSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsEmployer]
        else:
            permission_classes = [permissions.AllowAny]
        return [p() for p in permission_classes]

    def perform_create(self, serializer):
        serializer.save(employer=self.request.user)

class JobCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = JobCategory.objects.all()
    serializer_class = JobCategorySerializer

##############################
### FILE: jobs/urls.py
##############################

from rest_framework.routers import DefaultRouter
from .views import JobViewSet, JobCategoryViewSet

router = DefaultRouter()
router.register(r'', JobViewSet, basename='jobs')
router.register(r'categories', JobCategoryViewSet, basename='categories')

urlpatterns = router.urls

##############################
### FILE: applications/models.py
##############################

from django.db import models
from django.conf import settings
from jobs.models import Job

class Application(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_REVIEWED = 'reviewed'
    STATUS_REJECTED = 'rejected'
    STATUS_ACCEPTED = 'accepted'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_REVIEWED, 'Reviewed'),
        (STATUS_REJECTED, 'Rejected'),
        (STATUS_ACCEPTED, 'Accepted'),
    ]

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    job_seeker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='applications')
    resume = models.FileField(upload_to='resumes/')
    cover_letter = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Application by {self.job_seeker} for {self.job}"

##############################
### FILE: applications/serializers.py
##############################

from rest_framework import serializers
from .models import Application

class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ('id', 'job', 'job_seeker', 'resume', 'cover_letter', 'status', 'applied_at')
        read_only_fields = ('job_seeker', 'status', 'applied_at')

class ApplicationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ('status',)

##############################
### FILE: applications/views.py
##############################

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Application
from .serializers import ApplicationSerializer, ApplicationStatusSerializer

class IsJobSeeker(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == request.user.ROLE_SEEKER

class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all().order_by('-applied_at')
    serializer_class = ApplicationSerializer

    def get_permissions(self):
        if self.action in ['create']:
            permission_classes = [IsJobSeeker]
        elif self.action in ['update_status', 'list_for_employer']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [p() for p in permission_classes]

    def perform_create(self, serializer):
        serializer.save(job_seeker=self.request.user)
        # TODO: send notification to employer

    @action(detail=True, methods=['patch'], url_path='status')
    def update_status(self, request, pk=None):
        application = self.get_object()
        # Only employer who owns the job should update
        if application.job.employer != request.user:
            return Response({'detail': 'Not allowed'}, status=status.HTTP_403_FORBIDDEN)
        serializer = ApplicationStatusSerializer(application, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            # TODO: send notification to seeker
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='my')
    def my_applications(self, request):
        qs = Application.objects.filter(job_seeker=request.user)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='job/(?P<job_pk>[^/.]+)')
    def list_for_job(self, request, job_pk=None):
        # Employer: list applications for their job
        qs = Application.objects.filter(job_id=job_pk, job__employer=request.user)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

##############################
### FILE: applications/urls.py
##############################

from rest_framework.routers import DefaultRouter
from .views import ApplicationViewSet

router = DefaultRouter()
router.register(r'', ApplicationViewSet, basename='applications')

urlpatterns = router.urls

##############################
### FILE: reviews/models.py
##############################

from django.db import models
from django.conf import settings

class EmployerReview(models.Model):
    employer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_reviews')
    job_seeker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='given_reviews')
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review {self.rating} for {self.employer}"

##############################
### FILE: reviews/serializers.py
##############################

from rest_framework import serializers
from .models import EmployerReview

class EmployerReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployerReview
        fields = ('id', 'employer', 'job_seeker', 'rating', 'comment', 'created_at')
        read_only_fields = ('job_seeker', 'created_at')

##############################
### FILE: reviews/views.py
##############################

from rest_framework import viewsets, permissions
from .models import EmployerReview
from .serializers import EmployerReviewSerializer

class IsJobSeekerForReview(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == request.user.ROLE_SEEKER

class EmployerReviewViewSet(viewsets.ModelViewSet):
    queryset = EmployerReview.objects.all().order_by('-created_at')
    serializer_class = EmployerReviewSerializer

    def get_permissions(self):
        if self.action in ['create']:
            permission_classes = [IsJobSeekerForReview]
        else:
            permission_classes = [permissions.AllowAny]
        return [p() for p in permission_classes]

    def perform_create(self, serializer):
        serializer.save(job_seeker=self.request.user)

##############################
### FILE: reviews/urls.py
##############################

from rest_framework.routers import DefaultRouter
from .views import EmployerReviewViewSet

router = DefaultRouter()
router.register(r'', EmployerReviewViewSet, basename='reviews')

urlpatterns = router.urls

##############################
### FILE: notifications/utils.py (simple email helpers)
##############################

from django.core.mail import send_mail
from django.conf import settings

def send_application_received_email(to_email, job_title):
    subject = f"New application for {job_title}"
    message = f"You have received a new application for {job_title}. Log in to review it."
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [to_email])

def send_application_confirmation_email(to_email, job_title):
    subject = f"Application submitted: {job_title}"
    message = f"Your application for {job_title} has been submitted successfully."
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [to_email])

##############################
### FILE: README.md (short)
##############################

"""
JobBoardAPI - Django REST Framework scaffold

How to use:
1. pip install -r requirements.txt
2. Create Django project and apps as per tree.
3. Add settings snippets (AUTH_USER_MODEL etc.)
4. Run migrations: python manage.py makemigrations && python manage.py migrate
5. Create superuser and test endpoints.

Recommended extras:
- Integrate Celery for async emails
- Use S3/Cloudinary for resume storage in production
- Add rate limiting & file size/type validation for resumes
"""

##############################
### FILE: requirements.txt (suggested)
##############################

Django>=4.2
djangorestframework
djangorestframework-simplejwt
psycopg2-binary
python-dotenv
corsheaders


# End of scaffold
# Copy each FILE: block into the corresponding file in your project.
# If you want, I can now generate these files as separate downloadable files or a git repo scaffold.
