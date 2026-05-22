from rest_framework import serializers
from .models import (
    UserLearningProfile, TopicMastery, UserActivity,
    Recommendation, DailyTask, StudyPlan, StudyPlanDay,
    RevisionSchedule, LearningStreak
)


class UserLearningProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLearningProfile
        fields = [
            'id', 'target_exams', 'preferred_subjects', 'study_hours_per_day',
            'current_difficulty_level', 'learning_style', 'exam_date',
            'onboarding_completed', 'total_xp', 'level', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'total_xp', 'level', 'created_at', 'updated_at']


class TopicMasterySerializer(serializers.ModelSerializer):
    trend = serializers.SerializerMethodField()

    class Meta:
        model = TopicMastery
        fields = [
            'id', 'topic_name', 'subject', 'total_attempts', 'correct_answers',
            'accuracy_percentage', 'avg_time_per_question', 'confidence_score',
            'mastery_level', 'difficulty_level', 'last_practiced',
            'next_review_date', 'is_weak', 'is_improving', 'recent_scores', 'trend'
        ]
        read_only_fields = fields

    def get_trend(self, obj):
        scores = obj.recent_scores or []
        if len(scores) < 2:
            return 'stable'
        first = sum(scores[:len(scores)//2]) / max(len(scores)//2, 1)
        second = sum(scores[len(scores)//2:]) / max(len(scores) - len(scores)//2, 1)
        diff = second - first
        if diff > 5: return 'improving'
        elif diff < -5: return 'declining'
        return 'stable'


class UserActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserActivity
        fields = [
            'id', 'activity_type', 'resource_id', 'resource_type',
            'topic', 'subject', 'time_spent_seconds', 'score',
            'max_score', 'completed', 'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class RecommendationSerializer(serializers.ModelSerializer):
    resource_url = serializers.SerializerMethodField()

    class Meta:
        model = Recommendation
        fields = [
            'id', 'recommendation_type', 'title', 'description',
            'reason', 'reason_detail', 'relevance_score', 'priority_score',
            'confidence_score', 'final_score', 'topic', 'subject',
            'difficulty', 'resource_url', 'metadata',
            'is_dismissed', 'is_completed', 'created_at'
        ]
        read_only_fields = [
            'id', 'recommendation_type', 'title', 'description',
            'reason', 'reason_detail', 'relevance_score', 'priority_score',
            'confidence_score', 'final_score', 'topic', 'subject',
            'difficulty', 'resource_url', 'metadata', 'created_at'
        ]

    def get_resource_url(self, obj):
        if obj.resource_url and obj.resource_url.startswith('/media/'):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.resource_url)
            # Fallback if request is not passed in context
            return f"http://localhost:8000{obj.resource_url}"
        return obj.resource_url


class DailyTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyTask
        fields = [
            'id', 'date', 'task_type', 'title', 'description',
            'topic', 'subject', 'difficulty', 'is_completed',
            'completed_at', 'xp_reward', 'order'
        ]
        read_only_fields = [
            'id', 'date', 'task_type', 'title', 'description',
            'topic', 'subject', 'difficulty', 'completed_at', 'xp_reward', 'order'
        ]


class StudyPlanDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyPlanDay
        fields = [
            'id', 'day_number', 'date', 'title', 'tasks',
            'focus_topics', 'study_hours', 'is_revision_day',
            'is_mock_test_day', 'is_completed', 'completed_at'
        ]


class StudyPlanSerializer(serializers.ModelSerializer):
    days = StudyPlanDaySerializer(many=True, read_only=True)
    days_count = serializers.SerializerMethodField()

    class Meta:
        model = StudyPlan
        fields = [
            'id', 'title', 'target_exam', 'exam_date', 'start_date',
            'study_hours_per_day', 'weak_subjects', 'is_active',
            'progress_percentage', 'total_days', 'completed_days',
            'created_at', 'days', 'days_count'
        ]
        read_only_fields = [
            'id', 'title', 'progress_percentage', 'total_days',
            'completed_days', 'created_at', 'days'
        ]

    def get_days_count(self, obj):
        return obj.days.count()


class StudyPlanCreateSerializer(serializers.Serializer):
    target_exam = serializers.CharField(max_length=200)
    exam_date = serializers.DateField()
    patterns = serializers.CharField(max_length=300, required=False, allow_blank=True)
    topics_to_cover = serializers.ListField(
        child=serializers.CharField(), required=False, default=[]
    )
    marks_allotted = serializers.DictField(
        child=serializers.CharField(), required=False, default={}
    )
    study_hours_per_day = serializers.FloatField(default=2.0, required=False)
    weak_subjects = serializers.ListField(
        child=serializers.CharField(), required=False, default=[]
    )


class RevisionScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RevisionSchedule
        fields = [
            'id', 'topic', 'subject', 'review_date', 'interval_days',
            'repetition_number', 'is_completed', 'performance_rating'
        ]


class LearningStreakSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningStreak
        fields = [
            'id', 'current_streak', 'longest_streak', 'last_activity_date',
            'total_study_days', 'total_xp', 'level', 'weekly_xp',
            'monthly_xp', 'activity_calendar'
        ]
        read_only_fields = fields
