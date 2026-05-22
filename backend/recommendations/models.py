from django.db import models
from django.conf import settings
from django.utils import timezone
import json


class UserLearningProfile(models.Model):
    """Extended learning profile for AI personalization."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='learning_profile'
    )
    target_exams = models.JSONField(default=list, blank=True,
        help_text="List of target exam IDs")
    preferred_subjects = models.JSONField(default=list, blank=True)
    study_hours_per_day = models.FloatField(default=2.0)
    current_difficulty_level = models.CharField(
        max_length=20,
        choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')],
        default='intermediate'
    )
    learning_style = models.CharField(
        max_length=30,
        choices=[
            ('visual', 'Visual'), ('reading', 'Reading'),
            ('practice', 'Practice'), ('mixed', 'Mixed')
        ],
        default='mixed'
    )
    exam_date = models.DateField(blank=True, null=True,
        help_text="Target exam date for roadmap planning")
    onboarding_completed = models.BooleanField(default=False)
    total_xp = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rec_user_learning_profile'

    def __str__(self):
        return f"LearningProfile: {self.user.username}"


class TopicMastery(models.Model):
    """Tracks mastery level per topic per user."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='topic_masteries'
    )
    topic_name = models.CharField(max_length=200)
    subject = models.CharField(max_length=200, blank=True, default='')

    # Performance metrics
    total_attempts = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    accuracy_percentage = models.FloatField(default=0.0)
    avg_time_per_question = models.FloatField(default=0.0, help_text="Seconds")
    confidence_score = models.FloatField(default=50.0,
        help_text="0-100 confidence in this topic")
    mastery_level = models.CharField(
        max_length=20,
        choices=[
            ('novice', 'Novice'), ('learning', 'Learning'),
            ('proficient', 'Proficient'), ('expert', 'Expert')
        ],
        default='novice'
    )
    difficulty_level = models.CharField(
        max_length=20,
        choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')],
        default='medium'
    )

    # Spaced repetition
    last_practiced = models.DateTimeField(blank=True, null=True)
    next_review_date = models.DateTimeField(blank=True, null=True)
    repetition_interval = models.IntegerField(default=1, help_text="Days until next review")
    easiness_factor = models.FloatField(default=2.5, help_text="SM-2 easiness factor")
    repetition_count = models.IntegerField(default=0)

    # Trend tracking
    recent_scores = models.JSONField(default=list, blank=True,
        help_text="Last 10 accuracy scores for trend analysis")
    is_weak = models.BooleanField(default=False)
    is_improving = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rec_topic_mastery'
        unique_together = ('user', 'topic_name')
        indexes = [
            models.Index(fields=['user', 'is_weak']),
            models.Index(fields=['user', 'next_review_date']),
            models.Index(fields=['user', 'accuracy_percentage']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.topic_name} ({self.mastery_level})"

    def update_mastery(self):
        """Recalculate mastery level based on accuracy and attempts."""
        if self.total_attempts == 0:
            self.mastery_level = 'novice'
            self.is_weak = False
            return

        self.accuracy_percentage = (self.correct_answers / self.total_attempts) * 100

        if self.accuracy_percentage >= 85 and self.total_attempts >= 10:
            self.mastery_level = 'expert'
        elif self.accuracy_percentage >= 65 and self.total_attempts >= 5:
            self.mastery_level = 'proficient'
        elif self.accuracy_percentage >= 40:
            self.mastery_level = 'learning'
        else:
            self.mastery_level = 'novice'

        self.is_weak = self.accuracy_percentage < 50

        # Trend analysis
        if len(self.recent_scores) >= 3:
            recent = self.recent_scores[-3:]
            self.is_improving = recent[-1] > recent[0]

        self.save()


class UserActivity(models.Model):
    """Logs every user interaction for recommendation analysis."""
    ACTIVITY_TYPES = [
        ('quiz_attempt', 'Quiz Attempt'),
        ('resource_view', 'Resource View'),
        ('video_watch', 'Video Watch'),
        ('pdf_read', 'PDF Read'),
        ('mock_test', 'Mock Test'),
        ('flashcard_review', 'Flashcard Review'),
        ('note_view', 'Note View'),
        ('exam_page_visit', 'Exam Page Visit'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='learning_activities'
    )
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    resource_id = models.IntegerField(blank=True, null=True,
        help_text="ID of the related resource/quiz/exam")
    resource_type = models.CharField(max_length=50, blank=True, default='')
    topic = models.CharField(max_length=200, blank=True, default='')
    subject = models.CharField(max_length=200, blank=True, default='')

    # Engagement metrics
    time_spent_seconds = models.IntegerField(default=0)
    score = models.FloatField(blank=True, null=True)
    max_score = models.FloatField(blank=True, null=True)
    completed = models.BooleanField(default=False)

    metadata = models.JSONField(default=dict, blank=True,
        help_text="Additional context data")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'rec_user_activity'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'activity_type', '-created_at']),
            models.Index(fields=['user', 'topic']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.activity_type} - {self.topic}"


class Recommendation(models.Model):
    """AI-generated recommendation for a user."""
    RECOMMENDATION_TYPES = [
        ('quiz', 'Quiz'),
        ('pdf', 'PDF'),
        ('video', 'Video'),
        ('article', 'Article / Reference Site'),
        ('note', 'Note'),
        ('mock_test', 'Mock Test'),
        ('revision', 'Revision'),
        ('exam_update', 'Exam Update'),
        ('practice', 'Practice Set'),
    ]

    REASON_TYPES = [
        ('weak_topic', 'Weak Topic Improvement'),
        ('weak_topic_resource', 'Weak Topic Resource'),
        ('spaced_repetition', 'Spaced Repetition Review'),
        ('trending', 'Trending Content'),
        ('exam_relevant', 'Exam Relevant'),
        ('performance_based', 'Based on Performance'),
        ('interest_based', 'Based on Interests'),
        ('adaptive', 'Adaptive Difficulty'),
        ('daily_goal', 'Daily Goal'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='recommendations'
    )
    recommendation_type = models.CharField(max_length=50, choices=RECOMMENDATION_TYPES)
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True, default='')
    reason = models.CharField(max_length=50, choices=REASON_TYPES)
    reason_detail = models.CharField(max_length=300, blank=True, default='',
        help_text="Human readable explanation")

    # Scoring
    relevance_score = models.FloatField(default=0.0,
        help_text="0-100 relevance to user")
    priority_score = models.FloatField(default=0.0,
        help_text="0-100 urgency/priority")
    confidence_score = models.FloatField(default=0.0,
        help_text="0-100 recommendation confidence")
    final_score = models.FloatField(default=0.0,
        help_text="Weighted composite score for ranking")

    # Resource reference
    resource_id = models.IntegerField(blank=True, null=True)
    resource_type = models.CharField(max_length=50, blank=True, default='')
    resource_url = models.URLField(blank=True, default='')
    topic = models.CharField(max_length=200, blank=True, default='')
    subject = models.CharField(max_length=200, blank=True, default='')
    difficulty = models.CharField(
        max_length=20,
        choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')],
        default='medium'
    )

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    is_dismissed = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    expires_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'rec_recommendation'
        ordering = ['-final_score', '-created_at']
        indexes = [
            models.Index(fields=['user', '-final_score']),
            models.Index(fields=['user', 'recommendation_type']),
            models.Index(fields=['user', 'is_completed', 'is_dismissed']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.title} ({self.final_score:.0f})"


class DailyTask(models.Model):
    """AI-generated daily study tasks."""
    TASK_TYPES = [
        ('quiz', 'Complete Quiz'),
        ('revision', 'Revise Notes'),
        ('practice', 'Practice Questions'),
        ('mock_test', 'Take Mock Test'),
        ('video', 'Watch Video'),
        ('flashcard', 'Review Flashcards'),
        ('reading', 'Read Material'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='daily_tasks'
    )
    date = models.DateField(default=timezone.now)
    task_type = models.CharField(max_length=50, choices=TASK_TYPES)
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True, default='')
    topic = models.CharField(max_length=200, blank=True, default='')
    subject = models.CharField(max_length=200, blank=True, default='')
    difficulty = models.CharField(max_length=20, default='medium')

    # Progress
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)
    xp_reward = models.IntegerField(default=10)
    order = models.IntegerField(default=0)

    # Reference
    resource_id = models.IntegerField(blank=True, null=True)
    resource_type = models.CharField(max_length=50, blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'rec_daily_task'
        ordering = ['order', 'created_at']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['user', 'date', 'is_completed']),
        ]

    def __str__(self):
        status = "✔" if self.is_completed else "○"
        return f"{status} {self.user.username} - {self.title} ({self.date})"


class StudyPlan(models.Model):
    """AI-generated study roadmap."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='study_plans'
    )
    title = models.CharField(max_length=300)
    target_exam = models.CharField(max_length=200)
    exam_date = models.DateField()
    start_date = models.DateField(default=timezone.now)
    study_hours_per_day = models.FloatField(default=2.0)
    
    # New Fields for user input
    patterns = models.CharField(max_length=300, blank=True, default='')
    topics_to_cover = models.JSONField(default=list, blank=True)
    marks_allotted = models.JSONField(default=dict, blank=True)
    
    weak_subjects = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    progress_percentage = models.FloatField(default=0.0)
    total_days = models.IntegerField(default=0)
    completed_days = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rec_study_plan'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"

    def update_progress(self):
        total = self.days.count()
        completed = self.days.filter(is_completed=True).count()
        self.total_days = total
        self.completed_days = completed
        self.progress_percentage = (completed / total * 100) if total > 0 else 0
        self.save()


class StudyPlanDay(models.Model):
    """Individual day entry in a study plan."""
    plan = models.ForeignKey(
        StudyPlan, on_delete=models.CASCADE, related_name='days'
    )
    day_number = models.IntegerField()
    date = models.DateField()
    title = models.CharField(max_length=300)
    tasks = models.JSONField(default=list,
        help_text="List of task dicts: {type, title, topic, duration_minutes}")
    focus_topics = models.JSONField(default=list)
    study_hours = models.FloatField(default=2.0)
    is_revision_day = models.BooleanField(default=False)
    is_mock_test_day = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'rec_study_plan_day'
        ordering = ['day_number']
        unique_together = ('plan', 'day_number')

    def __str__(self):
        return f"Day {self.day_number}: {self.title}"


class RevisionSchedule(models.Model):
    """Spaced repetition review schedule."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='revision_schedules'
    )
    topic = models.CharField(max_length=200)
    subject = models.CharField(max_length=200, blank=True, default='')
    review_date = models.DateField()
    interval_days = models.IntegerField(default=1)
    repetition_number = models.IntegerField(default=1)
    is_completed = models.BooleanField(default=False)
    performance_rating = models.IntegerField(
        blank=True, null=True,
        help_text="0-5 rating of recall quality (SM-2)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'rec_revision_schedule'
        ordering = ['review_date']
        indexes = [
            models.Index(fields=['user', 'review_date', 'is_completed']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.topic} (Review: {self.review_date})"


class LearningStreak(models.Model):
    """Gamification — daily learning streak tracking."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='learning_streak'
    )
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_activity_date = models.DateField(blank=True, null=True)
    total_study_days = models.IntegerField(default=0)
    total_xp = models.IntegerField(default=0)
    level = models.IntegerField(default=1)

    # Weekly/Monthly stats
    weekly_xp = models.IntegerField(default=0)
    monthly_xp = models.IntegerField(default=0)
    activity_calendar = models.JSONField(default=dict, blank=True,
        help_text="Date->XP mapping for heatmap")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rec_learning_streak'

    def __str__(self):
        return f"{self.user.username} - Streak: {self.current_streak} days"

    def record_activity(self, xp_earned=10):
        """Record daily activity and update streak."""
        today = timezone.now().date()

        if self.last_activity_date == today:
            # Already recorded today, just add XP
            self.total_xp += xp_earned
            self.weekly_xp += xp_earned
            self.monthly_xp += xp_earned
        elif self.last_activity_date == today - timezone.timedelta(days=1):
            # Consecutive day
            self.current_streak += 1
            self.total_study_days += 1
            self.total_xp += xp_earned
            self.weekly_xp += xp_earned
            self.monthly_xp += xp_earned
        else:
            # Streak broken
            self.current_streak = 1
            self.total_study_days += 1
            self.total_xp += xp_earned
            self.weekly_xp += xp_earned
            self.monthly_xp += xp_earned

        if self.current_streak > self.longest_streak:
            self.longest_streak = self.current_streak

        self.last_activity_date = today
        self.level = (self.total_xp // 500) + 1

        # Update calendar
        cal = self.activity_calendar or {}
        date_key = today.isoformat()
        cal[date_key] = cal.get(date_key, 0) + xp_earned
        self.activity_calendar = cal

        self.save()


class DailyRevisionQuestion(models.Model):
    """Stores each wrongly-answered question during the day for end-of-day revision."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='daily_revision_questions'
    )
    date = models.DateField(default=timezone.now)

    # Question data (full snapshot from the quiz)
    question_text = models.TextField()
    question_type = models.CharField(max_length=30, default='mcq')
    options = models.JSONField(default=list, blank=True)
    correct_answer = models.CharField(max_length=500)
    user_answer = models.CharField(max_length=500, blank=True, default='')
    explanation = models.TextField(blank=True, default='')
    reference = models.TextField(blank=True, default='')
    topic = models.CharField(max_length=200, blank=True, default='')
    subject = models.CharField(max_length=200, blank=True, default='')
    difficulty = models.CharField(max_length=20, default='medium')

    # Source reference
    source_quiz_id = models.IntegerField(blank=True, null=True)
    source_quiz_title = models.CharField(max_length=300, blank=True, default='')

    # Revision status
    is_revised = models.BooleanField(default=False)
    revised_correctly = models.BooleanField(default=False)
    revised_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'rec_daily_revision_question'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'date', 'is_revised']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.question_text[:50]} ({self.date})"
