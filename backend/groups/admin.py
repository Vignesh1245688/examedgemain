from django.contrib import admin
from .models import Group, GroupMember, Message, Material

class GroupMemberInline(admin.TabularInline):
    model = GroupMember
    extra = 1

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'exam_type', 'exam_name', 'created_at')
    search_fields = ('name', 'exam_name')
    list_filter = ('exam_type',)
    inlines = [GroupMemberInline]

@admin.register(GroupMember)
class GroupMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'group', 'role', 'is_approved', 'joined_at')
    list_filter = ('role', 'is_approved')
    search_fields = ('user__username', 'group__name')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('group', 'sender', 'timestamp')
    list_filter = ('group', 'sender')

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'group', 'uploaded_by', 'timestamp')
    list_filter = ('group',)
