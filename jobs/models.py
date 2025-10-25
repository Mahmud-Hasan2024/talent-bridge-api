from django.conf import settings
from django.db import models

# Create your models here.

class JobCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.name
    
class Job(models.Model):
    Full_Time = 'full_time'
    Part_Time = 'part_time'
    Contract = 'contract'
    Internship = 'internship'
    Temporary = 'temporary'

    EMPLOYMENT_TYPE_CHOICES = [
        (Full_Time, 'Full Time'),
        (Part_Time, 'Part Time'),
        (Contract, 'Contract'),
        (Internship, 'Internship'),
        (Temporary, 'Temporary'),
    ]

    ENTRY_LEVEL = 'entry_level'
    MID_LEVEL = 'mid_level'
    SENIOR_LEVEL = 'senior_level'
    DIRECTOR = 'director'
    EXECUTIVE = 'executive'

    EXPERIENCE_LEVEL_CHOICES = [
        (ENTRY_LEVEL, 'Entry Level'),
        (MID_LEVEL, 'Mid Level'),
        (SENIOR_LEVEL, 'Senior Level'),
        (DIRECTOR, 'Director'),
        (EXECUTIVE, 'Executive'),
    ]

    ON_SITE = 'on_site'
    REMOTE = 'remote'
    HYBRID = 'hybrid'

    REMOTE_OPTION_CHOICES = [
        (ON_SITE, 'On-site'),
        (REMOTE, 'Remote'),
        (HYBRID, 'Hybrid'),
    ]

    employer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    description = models.TextField(max_length=5000)
    requirements = models.TextField(max_length=5000, blank=True)
    location = models.CharField(max_length=255, blank=True)
    category = models.ForeignKey(JobCategory, on_delete=models.SET_NULL, null=True, related_name='jobs')
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    application_deadline = models.DateField(null=True, blank=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    employment_type = models.CharField(max_length=50, choices=EMPLOYMENT_TYPE_CHOICES, default=Full_Time)
    experience_level = models.CharField(max_length=50, choices=EXPERIENCE_LEVEL_CHOICES, default=ENTRY_LEVEL)
    remote_option = models.CharField(max_length=50, choices=REMOTE_OPTION_CHOICES, default=ON_SITE)
    views_count = models.PositiveIntegerField(default=0)
    applications_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} at {self.company_name}"