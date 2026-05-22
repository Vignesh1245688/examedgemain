from django.urls import path
from .views import (
    PersonalizedFeedView, UpNextCarouselView, WeakTopicsView,
    DailyTasksView, StudyPlanView, StudyPlanDayCompleteView,
    AdvancedAnalyticsView, LearningProfileView, RevisionQueueView,
    StreakView, TrackActivityView, RecommendationActionView,
    DailyRevisionView, LeaderboardView
)

urlpatterns = [
    path('feed/', PersonalizedFeedView.as_view(), name='personalized-feed'),
    path('up-next/', UpNextCarouselView.as_view(), name='up-next-carousel'),
    path('weak-topics/', WeakTopicsView.as_view(), name='weak-topics'),
    path('daily-tasks/', DailyTasksView.as_view(), name='daily-tasks'),
    path('study-plan/', StudyPlanView.as_view(), name='study-plan'),
    path('study-plan/<int:plan_id>/day/<int:day_number>/complete/', StudyPlanDayCompleteView.as_view(), name='study-plan-day-complete'),
    path('analytics/', AdvancedAnalyticsView.as_view(), name='advanced-analytics'),
    path('learning-profile/', LearningProfileView.as_view(), name='learning-profile'),
    path('revision-queue/', RevisionQueueView.as_view(), name='revision-queue'),
    path('streak/', StreakView.as_view(), name='streak'),
    path('track-activity/', TrackActivityView.as_view(), name='track-activity'),
    path('action/<int:pk>/', RecommendationActionView.as_view(), name='recommendation-action'),
    path('daily-revision/', DailyRevisionView.as_view(), name='daily-revision'),
    path('leaderboard/', LeaderboardView.as_view(), name='leaderboard'),
]
