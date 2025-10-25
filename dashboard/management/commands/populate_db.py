# your_app/management/commands/populate_initial_data.py
from django.core.management.base import BaseCommand
from accounts.models import User
from jobs.models import JobCategory, Job
from applications.models import Application
from reviews.models import EmployerReview
from django.contrib.auth.models import Group
from faker import Faker
import random
from datetime import timedelta, date
from django.utils import timezone

fake = Faker()

class Command(BaseCommand):
    help = "Populate database with initial data"

    def handle(self, *args, **kwargs):
        self.stdout.write("Deleting old data...")
        Application.objects.all().delete()
        EmployerReview.objects.all().delete()
        Job.objects.all().delete()
        JobCategory.objects.all().delete()
        User.objects.all().delete()
        Group.objects.all().delete()

        # Create groups
        admin_group, _ = Group.objects.get_or_create(name="Admin")
        employer_group, _ = Group.objects.get_or_create(name="Employer")
        seeker_group, _ = Group.objects.get_or_create(name="Job Seeker")

        # Create users
        self.stdout.write("Creating users...")
        admins = []
        employers = []
        seekers = []

        # Admins
        for i in range(2):
            admin = User.objects.create_superuser(
                email=f"admin{i+1}@example.com",
                password="Admin123!",
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                role="admin",
            )
            admin.groups.add(admin_group)
            admins.append(admin)

        # Employers
        for i in range(5):
            employer = User.objects.create_user(
                email=f"employer{i+1}@example.com",
                password="Employer123!",
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                role="employer",
            )
            employer.groups.add(employer_group)
            employers.append(employer)

        # Job Seekers
        for i in range(20):
            seeker = User.objects.create_user(
                email=f"seeker{i+1}@example.com",
                password="Seeker123!",
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                role="seeker",
            )
            seeker.groups.add(seeker_group)
            seekers.append(seeker)

        # Create job categories
        self.stdout.write("Creating job categories...")
        categories = []
        category_names = ["Software", "Marketing", "Finance", "Design", "Sales"]
        for name in category_names:
            category = JobCategory.objects.create(
                name=name,
                description=fake.sentence()
            )
            categories.append(category)

        # Create jobs
        self.stdout.write("Creating jobs...")
        jobs = []
        for i in range(15):
            employer = random.choice(employers)
            category = random.choice(categories)
            job = Job.objects.create(
                employer=employer,
                title=fake.job(),
                company_name=fake.company(),
                description=fake.paragraph(nb_sentences=5),
                requirements=fake.paragraph(nb_sentences=3),
                location=fake.city(),
                category=category,
                is_featured=random.choice([True, False]),
                employment_type=random.choice([choice[0] for choice in Job.EMPLOYMENT_TYPE_CHOICES]),
                experience_level=random.choice([choice[0] for choice in Job.EXPERIENCE_LEVEL_CHOICES]),
                remote_option=random.choice([choice[0] for choice in Job.REMOTE_OPTION_CHOICES]),
                salary=random.randint(20000, 200000)
            )
            jobs.append(job)

        # Create applications
        self.stdout.write("Creating applications...")
        applications = []
        for job in jobs:
            num_applications = random.randint(1, 5)
            applied_seekers = random.sample(seekers, num_applications)
            for seeker in applied_seekers:
                status = random.choice([Application.PENDING, Application.REVIEWED, Application.INTERVIEWED, Application.OFFERED, Application.ACCEPTED])
                application = Application.objects.create(
                    job=job,
                    applicant=seeker,
                    resume="resumes/dummy.pdf",
                    status=status
                )
                applications.append(application)

        # Create reviews only for accepted applications
        self.stdout.write("Creating reviews...")
        for app in applications:
            if app.status == Application.ACCEPTED:
                EmployerReview.objects.create(
                    job=app.job,
                    employer=app.job.employer,
                    job_seeker=app.applicant,
                    rating=random.randint(3, 5),
                    comment=fake.sentence()
                )

        self.stdout.write(self.style.SUCCESS("Database populated successfully!"))
