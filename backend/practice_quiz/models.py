from django.db import models
from django.conf import settings

class QuizTemplate(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quiz_templates')
    name = models.CharField(max_length=255)
    config = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.name}"

class FlashcardSet(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='flashcard_sets')
    title = models.CharField(max_length=255)
    flashcards = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.title}"

class PracticeQuizResult(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='practice_quiz_results')
    title = models.CharField(max_length=255)
    file_name = models.CharField(max_length=255)
    score = models.IntegerField()
    total_questions = models.IntegerField()
    time_taken_seconds = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    # New fields for advanced analytics
    topics_accuracy = models.JSONField(default=dict, blank=True, null=True)
    question_analytics = models.JSONField(default=list, blank=True, null=True)
    weak_topics = models.JSONField(default=list, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.title} - {self.score}/{self.total_questions}"
