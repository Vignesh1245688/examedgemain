from rest_framework import serializers
from .models import NewsAlert

class NewsAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsAlert
        fields = '__all__'
