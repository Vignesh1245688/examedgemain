from django.urls import path
from .views import (
    PlatformAnalyticsView,
    UserListView, UserDetailView, UserActionView,
    ModerationQueueView, ModerationActionView,
    BroadcastNotificationView,
)

urlpatterns = [
    # Analytics
    path('analytics/', PlatformAnalyticsView.as_view(), name='admin-analytics'),
    
    # User Management
    path('users/', UserListView.as_view(), name='admin-users'),
    path('users/<int:user_id>/', UserDetailView.as_view(), name='admin-user-detail'),
    path('users/<int:user_id>/action/', UserActionView.as_view(), name='admin-user-action'),
    
    # Community Moderation
    path('moderation/', ModerationQueueView.as_view(), name='admin-moderation'),
    path('moderation/<int:resource_id>/action/', ModerationActionView.as_view(), name='admin-moderation-action'),
    
    # Notifications
    path('notifications/', BroadcastNotificationView.as_view(), name='admin-notifications'),
]
