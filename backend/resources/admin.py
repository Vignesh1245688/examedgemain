from django.contrib import admin
from .models import Resource

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'resource_type', 'exam', 'created_at')
    list_filter = ('resource_type', 'exam')
    search_fields = ('title',)
