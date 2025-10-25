from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from jobs.models import Job

class EmployerReview(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='reviews')
    employer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='employer_reviews')
    job_seeker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='job_seeker_reviews')
    rating = models.PositiveIntegerField(
        choices=[(i, i) for i in range(1, 6)],
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['employer', 'job_seeker', 'job'], name='unique_employer_review_per_job')
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"Review {self.rating} for {self.employer.first_name} by {self.job_seeker.first_name}"
