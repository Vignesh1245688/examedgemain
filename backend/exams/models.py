from django.db import models

from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Exam(models.Model):

    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='exams')
    conducting_body = models.CharField(max_length=200)
    eligibility = models.TextField(help_text="Age, education, nationality etc.")
    syllabus = models.TextField()
    official_link = models.URLField(blank=True, null=True)
    apply_link = models.URLField(blank=True, null=True, help_text="Direct link to application form")
    application_start_date = models.DateField(blank=True, null=True)
    application_end_date = models.DateField(blank=True, null=True)
    vacancies = models.IntegerField(blank=True, null=True)
    
    # User submission fields
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='uploaded_exams'
    )
    is_approved = models.BooleanField(
        default=True, help_text="Set to True by admin to publish this user-submitted exam"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ExamDate(models.Model):
    TYPE_CHOICES = (
        ('notification', 'Notification'),
        ('application_start', 'Application Start'),
        ('application_end', 'Application End'),
        ('exam', 'Exam Date'),
        ('result', 'Result Date')
    )
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='dates')
    date_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    date = models.DateField()

    def __str__(self):
        return f"{self.exam.name} - {self.get_date_type_display()} - {self.date}"
