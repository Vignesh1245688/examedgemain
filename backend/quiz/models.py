from django.db import models

class Question(models.Model):
    SUBJECT_CHOICES = (
        ('History', 'History'),
        ('Geography', 'Geography'),
        ('Polity', 'Polity'),
        ('Economy', 'Economy'),
        ('Current Affairs', 'Current Affairs'),
        ('State GK', 'State Specific GK'),
        ('General Science', 'General Science')
    )
    
    exam = models.ForeignKey('exams.Exam', on_delete=models.CASCADE, related_name='questions', blank=True, null=True)
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES)
    question_text = models.TextField()
    
    # Store options as A, B, C, D
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    
    CORRECT_CHOICES = (
        ('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')
    )
    correct_answer = models.CharField(max_length=1, choices=CORRECT_CHOICES)

    def __str__(self):
        return f"{self.subject}: {self.question_text[:50]}"

