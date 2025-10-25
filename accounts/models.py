from django.db import models
from django.contrib.auth.models import AbstractUser
from accounts.managers import CustomUserManager
from cloudinary.models import CloudinaryField

# Create your models here.

class User(AbstractUser):
    Admin = 'admin'
    Employer = 'employer'
    Job_Seeker = 'seeker'

    ROLE_CHOICES = [
        (Admin, 'Admin'),
        (Employer, 'Employer'),
        (Job_Seeker, 'Job Seeker'),
    ]

    username = None
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=Job_Seeker)
    address = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = CloudinaryField('profile_pictures', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    skills = models.TextField(max_length=5000, blank=True, null=True)
    education = models.TextField(max_length=5000, blank=True, null=True)
    experience = models.TextField(max_length=5000, blank=True, null=True)
    linkedin_profile = models.URLField(blank=True, null=True)
    github_profile = models.URLField(blank=True, null=True)
    portfolio_website = models.URLField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email