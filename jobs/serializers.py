from rest_framework import serializers
from jobs.models import Job, JobCategory

class JobCategorySerializer(serializers.ModelSerializer):
    job_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = JobCategory
        fields = ['id', 'name', 'description', 'job_count']
        read_only_fields = ['id', 'job_count']



class JobSerializer(serializers.ModelSerializer):
    category = JobCategorySerializer(read_only=True)

    category_id = serializers.PrimaryKeyRelatedField(
        queryset=JobCategory.objects.all(),
        source='category',
        write_only=True
    )

    class Meta:
        model = Job
        fields = [
            'id', 'employer', 'title', 'company_name', 'description', 'requirements', 
            'location', 'category', 'category_id', 'is_featured', 'created_at', 'employment_type', 
            'experience_level', 'remote_option', 'salary'
            ]
        
        read_only_fields = ['id', 'created_at']