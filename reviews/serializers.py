from rest_framework import serializers
from reviews.models import EmployerReview

class EmployerReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployerReview
        fields = [
            'id', 'job', 'job_seeker', 'employer',
            'rating', 'comment', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'job', 'job_seeker', 'employer',
            'created_at', 'updated_at'
        ]