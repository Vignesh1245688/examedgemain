from django.contrib import admin
from .models import (
    UserLearningProfile, TopicMastery, UserActivity,
    Recommendation, DailyTask, StudyPlan, StudyPlanDay,
    RevisionSchedule, LearningStreak
)


@admin.register(UserLearningProfile)
class UserLearningProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'current_difficulty_level', 'study_hours_per_day', 'level', 'total_xp']
    list_filter = ['current_difficulty_level', 'learning_style']
    search_fields = ['user__username']


@admin.register(TopicMastery)
class TopicMasteryAdmin(admin.ModelAdmin):
    list_display = ['user', 'topic_name', 'accuracy_percentage', 'mastery_level', 'is_weak', 'is_improving']
    list_filter = ['mastery_level', 'is_weak', 'difficulty_level']
    search_fields = ['user__username', 'topic_name']


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'activity_type', 'topic', 'time_spent_seconds', 'created_at']
    list_filter = ['activity_type']
    search_fields = ['user__username', 'topic']


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'recommendation_type', 'final_score', 'reason', 'is_completed']
    list_filter = ['recommendation_type', 'reason', 'is_completed']
    search_fields = ['user__username', 'title']


@admin.register(DailyTask)
class DailyTaskAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'task_type', 'date', 'is_completed', 'xp_reward']
    list_filter = ['task_type', 'is_completed', 'date']
    search_fields = ['user__username', 'title']


@admin.register(StudyPlan)
class StudyPlanAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'target_exam', 'progress_percentage', 'is_active']
    list_filter = ['is_active', 'target_exam']
    search_fields = ['user__username', 'title']


@admin.register(StudyPlanDay)
class StudyPlanDayAdmin(admin.ModelAdmin):
    list_display = ['plan', 'day_number', 'title', 'is_completed']
    list_filter = ['is_completed', 'is_revision_day', 'is_mock_test_day']


@admin.register(RevisionSchedule)
class RevisionScheduleAdmin(admin.ModelAdmin):
    list_display = ['user', 'topic', 'review_date', 'is_completed', 'repetition_number']
    list_filter = ['is_completed']
    search_fields = ['user__username', 'topic']


@admin.register(LearningStreak)
class LearningStreakAdmin(admin.ModelAdmin):
    list_display = ['user', 'current_streak', 'longest_streak', 'total_xp', 'level']
    search_fields = ['user__username']
