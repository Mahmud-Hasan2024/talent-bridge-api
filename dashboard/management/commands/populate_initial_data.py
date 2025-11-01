# your_app/management/commands/populate_initial_data.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from django.utils import timezone

from accounts.models import User
from jobs.models import JobCategory, Job
from applications.models import Application
from reviews.models import EmployerReview

from datetime import timedelta
import random

# Deterministic-ish randomness for timestamps (optional)
random.seed(42)

def _set_timestamp_if_field_exists(obj, dt):
    """
    Attempt to set a timestamp-like field on obj if it exists.
    Common field names: created_at, created_on, posted_at, posted_on,
    published_at, date_posted, applied_at, applied_on.
    Save the object if any field was set.
    """
    timestamp_fields = [
        "created_at", "created_on", "posted_at", "posted_on",
        "published_at", "date_posted", "applied_at", "applied_on",
        "applied_at", "applied_on", "applied_date", "date_applied"
    ]
    changed = False
    for fname in timestamp_fields:
        if hasattr(obj, fname):
            try:
                setattr(obj, fname, dt)
                changed = True
            except Exception:
                # ignore if field exists but can't be set
                pass
    if changed:
        try:
            obj.save()
        except Exception:
            # if saving fails for some reason, ignore — data already created
            pass

class Command(BaseCommand):
    help = "Delete all previous data and populate DB with a large hardcoded Bangladeshi-themed dataset with realistic timestamps."

    def handle(self, *args, **kwargs):
        now = timezone.now()

        self.stdout.write("🧹 Deleting old data...")
        # Clear previous content
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

        # -----------------------
        # USERS
        # -----------------------
        self.stdout.write("👥 Creating users with timestamps...")

        # Admins (3)
        admins_info = [
            ("admin1@dhakajobs.local", "Mahamud", "Hasan", "kgb12345"),
            ("admin2@dhakajobs.local", "Rashedul", "Shohel", "kgb12345"),
            ("admin3@dhakajobs.local", "Fatema", "Khatun", "kgb12345")
        ]
        admins = []
        for idx, (email, fn, ln, pw) in enumerate(admins_info):
            a = User.objects.create_superuser(
                email=email, password=pw, first_name=fn, last_name=ln, role="admin"
            )
            a.groups.add(admin_group)
            # realistic date_joined between 180-400 days ago
            dj = now - timedelta(days=180 + idx * 30 + random.randint(0, 20))
            if hasattr(a, "date_joined"):
                try:
                    a.date_joined = dj
                    a.save()
                except Exception:
                    pass
            admins.append(a)

        # Employers (8)
        employers_info = [
            ("recruit@dhakatech.com", "Dhaka", "Tech Ltd", "kgb12345"),
            ("hr@gulshansolutions.com", "Gulshan", "Solutions", "kgb12345"),
            ("careers@mirpursoft.com", "Mirpur", "Softworks", "kgb12345"),
            ("talent@chittagongit.com", "Chittagong", "IT Hub", "kgb12345"),
            ("jobs@rajshahicorp.com", "Rajshahi", "Corp", "kgb12345"),
            ("hello@sylhetdata.com", "Sylhet", "Data Labs", "kgb12345"),
            ("contact@banglaads.com", "Bangla", "Ads", "kgb12345"),
            ("hr@financebd.com", "Finance", "BD", "kgb12345")
        ]
        employers = []
        for idx, (email, fn, ln, pw) in enumerate(employers_info):
            emp = User.objects.create_user(
                email=email, password=pw, first_name=fn, last_name=ln, role="employer"
            )
            emp.groups.add(employer_group)
            # realistic date_joined between 90-350 days ago
            dj = now - timedelta(days=90 + idx * 12 + random.randint(0, 40))
            if hasattr(emp, "date_joined"):
                try:
                    emp.date_joined = dj
                    emp.save()
                except Exception:
                    pass
            employers.append(emp)

        # Job seekers (25)
        self.stdout.write("🧑‍💼 Creating job seekers with timestamps...")
        seekers_info = [
            ("seeker1@jobportal.local", "Arif", "Haque"),
            ("seeker2@jobportal.local", "Nusrat", "Akter"),
            ("seeker3@jobportal.local", "Tariq", "Islam"),
            ("seeker4@jobportal.local", "Nabila", "Rahman"),
            ("seeker5@jobportal.local", "Sajid", "Khan"),
            ("seeker6@jobportal.local", "Riad", "Siddique"),
            ("seeker7@jobportal.local", "Faria", "Chowdhury"),
            ("seeker8@jobportal.local", "Rakib", "Ahmed"),
            ("seeker9@jobportal.local", "Mita", "Begum"),
            ("seeker10@jobportal.local", "Sourav", "Roy"),
            ("seeker11@jobportal.local", "Meher", "Sultana"),
            ("seeker12@jobportal.local", "Biplob", "Kumar"),
            ("seeker13@jobportal.local", "Jannat", "Parvin"),
            ("seeker14@jobportal.local", "Kamal", "Hossain"),
            ("seeker15@jobportal.local", "Zara", "Islam"),
            ("seeker16@jobportal.local", "Tuhin", "Mia"),
            ("seeker17@jobportal.local", "Simran", "Akhtar"),
            ("seeker18@jobportal.local", "Anik", "Chandra"),
            ("seeker19@jobportal.local", "Lina", "Hasan"),
            ("seeker20@jobportal.local", "Rafi", "Khan"),
            ("seeker21@jobportal.local", "Nazmul", "Sakib"),
            ("seeker22@jobportal.local", "Popy", "Rahman"),
            ("seeker23@jobportal.local", "Ibrahim", "Deb"),
            ("seeker24@jobportal.local", "Polly", "Ahmed"),
            ("seeker25@jobportal.local", "Shamim", "Kibria")
        ]
        seekers = []
        for idx, (email, fn, ln) in enumerate(seekers_info):
            s = User.objects.create_user(
                email=email, password="kgb12345", first_name=fn, last_name=ln, role="seeker"
            )
            s.groups.add(seeker_group)
            # realistic date_joined between 5 and 200 days ago
            dj = now - timedelta(days=5 + (idx * 5) % 200)
            if hasattr(s, "date_joined"):
                try:
                    s.date_joined = dj
                    s.save()
                except Exception:
                    pass
            seekers.append(s)

        # -----------------------
        # JOB CATEGORIES (8)
        # -----------------------
        self.stdout.write("📂 Creating job categories...")
        categories_info = [
            ("Software Development", "Development roles for backend, frontend and full-stack engineers."),
            ("Digital Marketing", "SEO, SEM, social media and content marketing roles."),
            ("Finance & Accounting", "Accounting, auditing and financial analysis roles."),
            ("Graphic Design", "Design roles: UI/UX, graphic designers, visual artists."),
            ("Data Science", "Data engineering, analysis, machine learning roles."),
            ("Cybersecurity", "Security engineers, pentesters, SOC analysts."),
            ("Customer Support", "Call center, live chat and customer success roles."),
            ("Human Resources", "Recruitment, HR operations and talent management.")
        ]
        categories = {}
        for idx, (name, desc) in enumerate(categories_info):
            c = JobCategory.objects.create(name=name, description=desc)
            # optionally set timestamps if the category model has them
            cat_dt = now - timedelta(days=200 - idx * 10)
            _set_timestamp_if_field_exists(c, cat_dt)
            categories[name] = c

        # -----------------------
        # JOBS (~40) + timestamps
        # -----------------------
        self.stdout.write("💼 Creating jobs (many entries) with posted timestamps...")
        jobs_data = [
            (0, "Backend Developer (Python/Django)", "Dhaka Tech Ltd.", "Build and maintain Django-based backend services for web products.", "Python, Django, DRF, PostgreSQL, REST APIs", "Gulshan, Dhaka", "Software Development", True, "full_time", "mid", "hybrid", 90000),
            (0, "Frontend Developer (React)", "Dhaka Tech Ltd.", "Create responsive UI components and collaborate with designers.", "React, JS, HTML/CSS, REST integration", "Baridhara, Dhaka", "Software Development", False, "full_time", "junior", "hybrid", 70000),
            (0, "DevOps Engineer", "Dhaka Tech Ltd.", "Maintain CI/CD, cloud infra, and monitoring.", "Docker, Kubernetes, AWS/GCP, CI/CD", "Uttara, Dhaka", "Software Development", True, "full_time", "senior", "onsite", 130000),

            (1, "Graphic Designer", "Gulshan Solutions", "Design marketing creatives and UI assets.", "Adobe Suite, Figma, portfolio", "Gulshan, Dhaka", "Graphic Design", False, "contract", "junior", "remote", 45000),
            (1, "Digital Marketing Manager", "Gulshan Solutions", "Lead marketing campaigns and strategy.", "SEO, Google Ads, content strategy", "Gulshan, Dhaka", "Digital Marketing", True, "full_time", "senior", "onsite", 110000),

            (2, "Full Stack Developer", "Mirpur Softworks", "End-to-end feature implementation for web apps.", "Python/Django + React", "Mirpur, Dhaka", "Software Development", False, "full_time", "mid", "hybrid", 85000),
            (2, "Customer Support Engineer", "Mirpur Softworks", "Assist users and troubleshoot technical issues.", "Good communication, basic technical skills", "Mirpur, Dhaka", "Customer Support", False, "full_time", "junior", "onsite", 35000),

            (3, "Data Analyst", "Chittagong IT Hub", "Analyze datasets and produce dashboards.", "SQL, Excel, Power BI/Tableau", "Pahartali, Chittagong", "Data Science", False, "full_time", "mid", "onsite", 80000),
            (3, "Machine Learning Engineer", "Chittagong IT Hub", "Develop ML models and pipelines.", "Python, scikit-learn, model deployment", "Pahartali, Chittagong", "Data Science", True, "full_time", "senior", "hybrid", 140000),

            (4, "Accountant", "Rajshahi Corp", "Manage accounts, payroll and reconciliation.", "Tally/Excel, financial reporting", "Rajshahi City", "Finance & Accounting", False, "full_time", "mid", "onsite", 60000),
            (4, "Finance Officer", "Rajshahi Corp", "Financial planning and budget monitoring.", "Forecasting, Excel, accounting principles", "Rajshahi City", "Finance & Accounting", True, "full_time", "senior", "onsite", 90000),

            (5, "Security Analyst (SOC)", "Sylhet Data Labs", "Monitor security alerts and triage incidents.", "SIEM, incident response, Linux", "Sylhet City", "Cybersecurity", False, "full_time", "junior", "onsite", 70000),
            (5, "Penetration Tester", "Sylhet Data Labs", "Conduct pentests and report vulnerabilities.", "OSCP or equivalent, web pentesting", "Sylhet City", "Cybersecurity", True, "contract", "senior", "onsite", 150000),

            (6, "Social Media Executive", "Bangla Ads", "Manage social media calendar and creatives.", "Social media platforms, content scheduling", "Dhanmondi, Dhaka", "Digital Marketing", False, "full_time", "junior", "remote", 42000),
            (6, "Content Writer", "Bangla Ads", "Write blog posts, ad copies and case studies.", "Strong Bangla & English writing skills", "Dhanmondi, Dhaka", "Digital Marketing", False, "contract", "mid", "remote", 38000),

            (7, "Financial Analyst", "Finance BD", "Perform company financial analysis and valuation.", "Excel, financial modelling, reporting", "Motijheel, Dhaka", "Finance & Accounting", True, "full_time", "mid", "onsite", 95000),
            (7, "Payroll Executive", "Finance BD", "Handle payroll and statutory compliance.", "Payroll systems, attention to detail", "Motijheel, Dhaka", "Human Resources", False, "full_time", "junior", "onsite", 42000),

            (0, "API Engineer", "Dhaka Tech Ltd.", "Design and maintain public/internal APIs.", "RESTful design, OpenAPI, testing", "Banani, Dhaka", "Software Development", False, "full_time", "mid", "hybrid", 88000),
            (1, "UX Designer", "Gulshan Solutions", "Design user journeys and wireframes.", "Figma, user research, prototyping", "Gulshan, Dhaka", "Graphic Design", False, "full_time", "mid", "hybrid", 82000),
            (2, "Support Manager", "Mirpur Softworks", "Lead the support team and SLA adherence.", "Team management, CRM experience", "Mirpur, Dhaka", "Customer Support", True, "full_time", "senior", "onsite", 100000),
            (3, "Data Engineer", "Chittagong IT Hub", "Build ETL pipelines and data warehouses.", "Python, Airflow, Redshift/BigQuery", "Pahartali, Chittagong", "Data Science", False, "full_time", "senior", "onsite", 135000),
            (4, "Audit Associate", "Rajshahi Corp", "Assist in financial audits and documentation.", "Audit standards, attention to detail", "Rajshahi City", "Finance & Accounting", False, "full_time", "junior", "onsite", 48000),
            (5, "Cloud Engineer", "Sylhet Data Labs", "Manage cloud infrastructure and costs.", "AWS/GCP, infra as code", "Sylhet City", "Software Development", True, "full_time", "mid", "hybrid", 125000),
            (6, "SEO Specialist", "Bangla Ads", "Improve organic search performance.", "SEO tools, on-page and technical SEO", "Dhanmondi, Dhaka", "Digital Marketing", False, "contract", "mid", "remote", 60000),
            (7, "HR Generalist", "Finance BD", "Handle HR ops, recruitment and onboarding.", "Recruitment cycle, HR policies", "Motijheel, Dhaka", "Human Resources", False, "full_time", "mid", "onsite", 65000),

            (0, "Software Tester (QA)", "Dhaka Tech Ltd.", "Build test cases and automate tests.", "Selenium, pytest, testing methodologies", "Gulshan, Dhaka", "Software Development", False, "full_time", "junior", "onsite", 55000),
            (1, "Brand Strategist", "Gulshan Solutions", "Define brand direction and campaigns.", "Branding, market research", "Gulshan, Dhaka", "Digital Marketing", False, "full_time", "senior", "onsite", 115000),
            (2, "Mobile App Developer", "Mirpur Softworks", "Build Android/iOS apps using Flutter.", "Flutter, Dart, mobile architecture", "Mirpur, Dhaka", "Software Development", False, "full_time", "mid", "hybrid", 90000),
            (3, "BI Developer", "Chittagong IT Hub", "Create dashboards and ETL for business users.", "Power BI/Tableau, SQL", "Pahartali, Chittagong", "Data Science", False, "contract", "mid", "onsite", 78000),

            (4, "Tax Specialist", "Rajshahi Corp", "Manage tax filing and compliance.", "Tax rules, filings", "Rajshahi City", "Finance & Accounting", False, "full_time", "senior", "onsite", 98000),
            (5, "Incident Responder", "Sylhet Data Labs", "Respond to security incidents and recovery.", "IR process, forensics basics", "Sylhet City", "Cybersecurity", False, "full_time", "mid", "onsite", 95000),
            (6, "Customer Success Manager", "Bangla Ads", "Onboard clients and ensure retention.", "Account management, communication", "Dhanmondi, Dhaka", "Customer Support", True, "full_time", "senior", "onsite", 105000),
            (7, "Recruitment Specialist", "Finance BD", "Coordinate hiring and interviews.", "Sourcing, interviewing", "Motijheel, Dhaka", "Human Resources", False, "full_time", "junior", "onsite", 48000),

            (0, "Site Reliability Engineer", "Dhaka Tech Ltd.", "Ensure system reliability and uptime.", "SRE practices, monitoring, SLA", "Uttara, Dhaka", "Software Development", True, "full_time", "senior", "onsite", 145000),
            (1, "Motion Graphics Artist", "Gulshan Solutions", "Create motion ads and short videos.", "After Effects, storytelling", "Gulshan, Dhaka", "Graphic Design", False, "contract", "mid", "remote", 54000),
            (2, "Technical Writer", "Mirpur Softworks", "Write technical docs and API guides.", "Writing, ability to explain code", "Mirpur, Dhaka", "Software Development", False, "contract", "mid", "remote", 52000),
            (3, "Research Analyst", "Chittagong IT Hub", "Market research and competitor analysis.", "Research skills, reporting", "Pahartali, Chittagong", "Data Science", False, "full_time", "junior", "onsite", 46000),
        ]

        jobs = []
        for i, jd in enumerate(jobs_data):
            (
                employer_idx, title, company_name, description, requirements,
                location, category_name, is_featured, employment_type,
                experience_level, remote_option, salary
            ) = jd
            employer_obj = employers[employer_idx]
            category_obj = categories[category_name]

            job = Job.objects.create(
                employer=employer_obj,
                title=title,
                company_name=company_name,
                description=description,
                requirements=requirements,
                location=location,
                category=category_obj,
                is_featured=is_featured,
                employment_type=employment_type,
                experience_level=experience_level,
                remote_option=remote_option,
                salary=salary
            )

            # realistic posted date: 10 - 60 days ago
            posted_dt = now - timedelta(days=random.randint(10, 60))
            _set_timestamp_if_field_exists(job, posted_dt)

            # If job model has a "published" boolean or "is_active" field, we could set it; skip to keep safe.
            jobs.append(job)

        # -----------------------
        # APPLICATIONS (2-4 per job) + timestamps
        # -----------------------
        self.stdout.write("✉️ Creating applications with realistic timestamps...")
        statuses = [
            Application.PENDING,
            Application.REVIEWED,
            Application.INTERVIEWED,
            Application.OFFERED,
            Application.ACCEPTED
        ]
        applications = []
        seeker_count = len(seekers)

        for i, job in enumerate(jobs):
            # number of applicants: deterministic 2..4 pattern
            num_apps = 2 + (i % 3)  # yields 2,3,4 pattern
            # determine index base
            base_idx = (i * 2) % seeker_count
            # figure out job posted date for application window; fallback to now - 20 days
            job_posted = None
            # Try to retrieve one of the common timestamp fields
            for fname in ("created_at", "posted_at", "published_at", "date_posted", "posted_on"):
                if hasattr(job, fname):
                    job_posted = getattr(job, fname)
                    break
            if job_posted is None:
                # fallback: approximate from now
                job_posted = now - timedelta(days=random.randint(10, 60))

            for j in range(num_apps):
                seeker_idx = (base_idx + j) % seeker_count
                seeker_obj = seekers[seeker_idx]
                # status cycles deterministically
                status = statuses[(i + j) % len(statuses)]

                # application timestamp: 3 - 20 days after job_posted (but not in future)
                delta_days = random.randint(3, 20)
                applied_dt = job_posted + timedelta(days=delta_days)
                # clamp to now
                if applied_dt > now:
                    applied_dt = now - timedelta(hours=random.randint(1, 48))

                resume_path = f"resumes/{seeker_obj.first_name.lower()}_{seeker_obj.last_name.lower()}.pdf"
                app = Application.objects.create(
                    job=job,
                    applicant=seeker_obj,
                    resume=resume_path,
                    status=status
                )
                _set_timestamp_if_field_exists(app, applied_dt)

                applications.append(app)

        # -----------------------
        # EMPLOYER REVIEWS (only for ACCEPTED applications) + timestamps
        # -----------------------
        self.stdout.write("⭐ Creating employer reviews for ACCEPTED applications with timestamps...")
        for app in applications:
            if app.status == Application.ACCEPTED:
                # review created 1-7 days after acceptance (application date)
                app_dt = None
                for fname in ("created_at", "applied_at", "applied_on", "date_applied"):
                    if hasattr(app, fname):
                        app_dt = getattr(app, fname)
                        break
                if app_dt is None:
                    # fallback to now - small offset
                    app_dt = now - timedelta(days=random.randint(1, 14))

                rev_dt = app_dt + timedelta(days=random.randint(1, 7))
                if rev_dt > now:
                    rev_dt = now - timedelta(hours=random.randint(1, 48))

                comment = (
                    f"{app.applicant.first_name} demonstrated professionalism and delivered required work "
                    f"for the role '{app.job.title}'. Recommended for future projects."
                )
                rating = 4
                # deterministic variation: make some 5-star based on name length
                if (len(app.applicant.first_name) % 2) == 0:
                    rating = 5

                review = EmployerReview.objects.create(
                    job=app.job,
                    employer=app.job.employer,
                    job_seeker=app.applicant,
                    rating=rating,
                    comment=comment
                )
                _set_timestamp_if_field_exists(review, rev_dt)

        self.stdout.write(self.style.SUCCESS("✅ Database populated successfully with hardcoded Bangladeshi-themed data and realistic timestamps!"))
