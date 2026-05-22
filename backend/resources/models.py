from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


def resource_upload_path(instance, filename):
    """Dynamic upload path: PDFs → resources/pdfs/, Videos → resources/videos/"""
    if instance.resource_type == 'video':
        return f'resources/videos/{filename}'
    return f'resources/pdfs/{filename}'


class Resource(models.Model):
    TYPE_CHOICES = (
        ('pdf', 'PDF Document'),
        ('video', 'Video Link / File'),
        ('article', 'Article Link')
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True, help_text="Short description of the resource")
    resource_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    subject = models.CharField(max_length=200, blank=True, default='', help_text="Subject/topic tag for AI matching")
    url = models.URLField(max_length=500, blank=True, null=True, help_text="Link to the PDF, video or article")
    file = models.FileField(upload_to=resource_upload_path, blank=True, null=True, help_text="Upload PDF or video file directly")
    exam = models.ForeignKey('exams.Exam', on_delete=models.CASCADE, related_name='resources', blank=True, null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='uploaded_resources')
    view_count = models.PositiveIntegerField(default=0, help_text="Number of times this resource was viewed")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.get_resource_type_display()})"
