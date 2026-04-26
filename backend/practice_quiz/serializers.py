from rest_framework import serializers
from .models import PracticeQuizResult

class PracticeQuizResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = PracticeQuizResult
        fields = ['id', 'user', 'title', 'file_name', 'score', 'total_questions', 'time_taken_seconds', 'created_at']
        read_only_fields = ['user']
