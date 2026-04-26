from rest_framework import serializers
from .models import Question

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'subject', 'question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer']
        # Note: in real prod, we might hide correct_answer in the base payload and only return it on submission
