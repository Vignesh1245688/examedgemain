from django.contrib import admin
from .models import Question

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('subject', 'exam', 'question_text')
    list_filter = ('subject', 'exam')
    search_fields = ('question_text',)
