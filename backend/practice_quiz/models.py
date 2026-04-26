from django.db import models
from django.conf import settings

class PracticeQuizResult(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='practice_quiz_results')
    title = models.CharField(max_length=255)
    file_name = models.CharField(max_length=255)
    score = models.IntegerField()
    total_questions = models.IntegerField()
    time_taken_seconds = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.title} - {self.score}/{self.total_questions}"
