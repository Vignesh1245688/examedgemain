from rest_framework import serializers
from .models import PracticeQuizResult, QuizTemplate, FlashcardSet

class PracticeQuizResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = PracticeQuizResult
        fields = ['id', 'user', 'title', 'file_name', 'score', 'total_questions', 'time_taken_seconds', 'topics_accuracy', 'question_analytics', 'weak_topics', 'created_at']
        read_only_fields = ['user']

class QuizTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizTemplate
        fields = ['id', 'user', 'name', 'config', 'created_at']
        read_only_fields = ['user']

class FlashcardSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlashcardSet
        fields = ['id', 'user', 'title', 'flashcards', 'created_at']
        read_only_fields = ['user']
