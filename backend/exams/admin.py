from django.contrib import admin
from .models import Exam, ExamDate

class ExamDateInline(admin.TabularInline):
    model = ExamDate
    extra = 1

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'conducting_body', 'vacancies')
    list_filter = ('category',)
    search_fields = ('name', 'conducting_body')
    inlines = [ExamDateInline]
