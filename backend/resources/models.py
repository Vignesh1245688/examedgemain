from django.db import models

class Resource(models.Model):
    TYPE_CHOICES = (
        ('pdf', 'PDF Document'),
        ('video', 'Video Link'),
        ('article', 'Article Link')
    )

    title = models.CharField(max_length=255)
    resource_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    url = models.URLField(max_length=500, help_text="Link to the PDF, video or article")
    exam = models.ForeignKey('exams.Exam', on_delete=models.CASCADE, related_name='resources', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.get_resource_type_display()})"

