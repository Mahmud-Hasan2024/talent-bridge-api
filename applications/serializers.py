from rest_framework import serializers
from applications.models import Application

class ApplicationSerializer(serializers.ModelSerializer):
    applicant = serializers.StringRelatedField(read_only=True)
    job = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Application
        fields = [ 'id', 'job', 'applicant', 'cover_letter', 'resume', 
                  'portfolio_link', 'applied_at', 'status']
        
        read_only_fields = ['applied_at', 'status']
