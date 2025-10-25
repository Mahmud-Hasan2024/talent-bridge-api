from django_filters.rest_framework import FilterSet
from jobs.models import Job


class JobFilter(FilterSet):
    class Meta:
        model = Job
        fields = {
            'category_id': ['exact'],
            'salary': ['gt', 'lt']
        }