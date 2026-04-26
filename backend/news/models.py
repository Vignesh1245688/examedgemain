from django.db import models

class NewsAlert(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    exam = models.ForeignKey('exams.Exam', on_delete=models.CASCADE, related_name='news_alerts', blank=True, null=True)
    link = models.URLField(max_length=500, blank=True, null=True, help_text="Link to official notification")
    date_posted = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

