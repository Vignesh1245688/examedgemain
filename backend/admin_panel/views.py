from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from django.db.models import Count, Avg, Q, Sum
from django.db.models.functions import TruncDate
from datetime import timedelta

from .permissions import IsStaffUser, IsSuperAdmin
from users.models import User, Profile, Notification
from recommendations.models import (
    LearningStreak, TopicMastery, UserActivity,
    Recommendation, DailyTask, StudyPlan
)
from resources.models import Resource


# ═══════════════════════════════════════════════════════════════
# MODULE 1 — PLATFORM ANALYTICS DASHBOARD
# ═══════════════════════════════════════════════════════════════

class PlatformAnalyticsView(APIView):
    """Real-time platform KPIs and analytics."""
    permission_classes = [IsStaffUser]

    def get(self, request):
        now = timezone.now()
        today = now.date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)

        # ── KPIs ──
        total_users = User.objects.count()
        
        # DAU: users with activity today
        dau = UserActivity.objects.filter(
            created_at__date=today
        ).values('user').distinct().count()
        
        # WAU: users with activity this week
        wau = UserActivity.objects.filter(
            created_at__date__gte=week_ago
        ).values('user').distinct().count()

        # XP stats
        xp_stats = LearningStreak.objects.aggregate(
            avg_xp=Avg('total_xp'),
            total_xp=Sum('total_xp'),
            avg_streak=Avg('current_streak'),
            max_streak=Avg('longest_streak'),
        )

        # Streak distribution
        streak_dist = {
            '0_days': LearningStreak.objects.filter(current_streak=0).count(),
            '1_3_days': LearningStreak.objects.filter(current_streak__gte=1, current_streak__lte=3).count(),
            '4_7_days': LearningStreak.objects.filter(current_streak__gte=4, current_streak__lte=7).count(),
            '8_14_days': LearningStreak.objects.filter(current_streak__gte=8, current_streak__lte=14).count(),
            '15_plus': LearningStreak.objects.filter(current_streak__gte=15).count(),
        }

        # ── AI Insights ──
        # Weak subject heatmap: topics most users are weak in
        weak_topics = (
            TopicMastery.objects.filter(is_weak=True)
            .values('topic_name')
            .annotate(weak_count=Count('id'))
            .order_by('-weak_count')[:10]
        )
        total_mastery_users = TopicMastery.objects.values('user').distinct().count() or 1
        weak_heatmap = [
            {
                'topic': t['topic_name'],
                'weak_count': t['weak_count'],
                'percentage': round(t['weak_count'] / total_mastery_users * 100, 1),
            }
            for t in weak_topics
        ]

        # ── Content Stats ──
        total_resources = Resource.objects.count()
        total_pdfs = Resource.objects.filter(resource_type='pdf').count()
        total_videos = Resource.objects.filter(resource_type='video').count()
        community_uploads = Resource.objects.filter(uploaded_by__isnull=False).count()

        # Activity over last 14 days (for chart)
        activity_chart = list(
            UserActivity.objects.filter(created_at__date__gte=today - timedelta(days=14))
            .annotate(day=TruncDate('created_at'))
            .values('day')
            .annotate(count=Count('id'))
            .order_by('day')
        )
        # Convert date to string for JSON
        for item in activity_chart:
            item['day'] = item['day'].isoformat()

        # New users over last 14 days
        new_users_chart = list(
            User.objects.filter(date_joined__date__gte=today - timedelta(days=14))
            .annotate(day=TruncDate('date_joined'))
            .values('day')
            .annotate(count=Count('id'))
            .order_by('day')
        )
        for item in new_users_chart:
            item['day'] = item['day'].isoformat()

        return Response({
            'kpis': {
                'total_users': total_users,
                'dau': dau,
                'wau': wau,
                'avg_xp': round(xp_stats['avg_xp'] or 0, 1),
                'total_xp': xp_stats['total_xp'] or 0,
                'avg_streak': round(xp_stats['avg_streak'] or 0, 1),
            },
            'streak_distribution': streak_dist,
            'weak_heatmap': weak_heatmap,
            'content_stats': {
                'total_resources': total_resources,
                'pdfs': total_pdfs,
                'videos': total_videos,
                'community_uploads': community_uploads,
            },
            'activity_chart': activity_chart,
            'new_users_chart': new_users_chart,
        })


# ═══════════════════════════════════════════════════════════════
# MODULE 2 — USER MANAGEMENT
# ═══════════════════════════════════════════════════════════════

class UserListView(APIView):
    """Searchable, paginated user list."""
    permission_classes = [IsStaffUser]

    def get(self, request):
        search = request.query_params.get('search', '')
        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('per_page', 20))

        qs = User.objects.select_related('profile').all().order_by('-date_joined')
        
        if search:
            qs = qs.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )

        total = qs.count()
        start = (page - 1) * per_page
        users = qs[start:start + per_page]

        data = []
        for u in users:
            try:
                streak = u.learning_streak
                xp = streak.total_xp
                level = streak.level
                current_streak = streak.current_streak
            except LearningStreak.DoesNotExist:
                xp = 0
                level = 1
                current_streak = 0

            data.append({
                'id': u.id,
                'username': u.username,
                'email': u.email,
                'first_name': u.first_name,
                'last_name': u.last_name,
                'is_active': u.is_active,
                'is_staff': u.is_staff,
                'date_joined': u.date_joined.isoformat(),
                'target_exam': getattr(u.profile, 'target_exam', '') if hasattr(u, 'profile') else '',
                'xp': xp,
                'level': level,
                'streak': current_streak,
            })

        return Response({
            'users': data,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page,
        })


class UserDetailView(APIView):
    """View full details of a single user."""
    permission_classes = [IsStaffUser]

    def get(self, request, user_id):
        try:
            u = User.objects.select_related('profile').get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Streak
        try:
            streak = LearningStreak.objects.get(user=u)
            streak_data = {
                'current_streak': streak.current_streak,
                'longest_streak': streak.longest_streak,
                'total_xp': streak.total_xp,
                'level': streak.level,
                'total_study_days': streak.total_study_days,
            }
        except LearningStreak.DoesNotExist:
            streak_data = {'current_streak': 0, 'longest_streak': 0, 'total_xp': 0, 'level': 1, 'total_study_days': 0}

        # Topic mastery
        masteries = TopicMastery.objects.filter(user=u).order_by('-accuracy_percentage')[:10]
        mastery_data = [
            {'topic': m.topic_name, 'accuracy': round(m.accuracy_percentage, 1), 'is_weak': m.is_weak, 'mastery': m.mastery_level}
            for m in masteries
        ]

        # Recent activity
        activities = UserActivity.objects.filter(user=u).order_by('-created_at')[:20]
        activity_data = [
            {'type': a.activity_type, 'topic': a.topic, 'score': a.score, 'date': a.created_at.isoformat()}
            for a in activities
        ]

        return Response({
            'user': {
                'id': u.id, 'username': u.username, 'email': u.email,
                'first_name': u.first_name, 'last_name': u.last_name,
                'is_active': u.is_active, 'is_staff': u.is_staff,
                'date_joined': u.date_joined.isoformat(),
                'target_exam': getattr(u.profile, 'target_exam', '') if hasattr(u, 'profile') else '',
            },
            'streak': streak_data,
            'mastery': mastery_data,
            'recent_activity': activity_data,
        })


class UserActionView(APIView):
    """Admin actions: block/unblock users."""
    permission_classes = [IsSuperAdmin]

    def post(self, request, user_id):
        action = request.data.get('action')
        try:
            u = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        if action == 'block':
            u.is_active = False
            u.save()
            return Response({'status': 'User blocked', 'is_active': False})
        elif action == 'unblock':
            u.is_active = True
            u.save()
            return Response({'status': 'User unblocked', 'is_active': True})
        elif action == 'make_staff':
            u.is_staff = True
            u.save()
            return Response({'status': 'User promoted to staff', 'is_staff': True})
        elif action == 'remove_staff':
            u.is_staff = False
            u.save()
            return Response({'status': 'Staff access removed', 'is_staff': False})

        return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)


# ═══════════════════════════════════════════════════════════════
# MODULE 3 — COMMUNITY MODERATION
# ═══════════════════════════════════════════════════════════════

class ModerationQueueView(APIView):
    """View pending community uploads for approval."""
    permission_classes = [IsStaffUser]

    def get(self, request):
        filter_status = request.query_params.get('status', 'pending')
        
        qs = Resource.objects.filter(uploaded_by__isnull=False).order_by('-created_at')
        
        # We'll use a simple metadata-based status system
        # Resources with is_approved field (we'll need to check/add this)
        resources = qs[:50]
        
        data = []
        for r in resources:
            data.append({
                'id': r.id,
                'title': r.title,
                'resource_type': r.resource_type,
                'url': r.url,
                'file_url': r.file.url if r.file else None,
                'description': getattr(r, 'description', ''),
                'uploaded_by': r.uploaded_by.username if r.uploaded_by else 'System',
                'uploaded_by_id': r.uploaded_by.id if r.uploaded_by else None,
                'created_at': r.created_at.isoformat(),
            })

        return Response({'resources': data, 'total': len(data)})


class ModerationActionView(APIView):
    """Approve, reject, or delete a community resource."""
    permission_classes = [IsStaffUser]

    def post(self, request, resource_id):
        action = request.data.get('action')
        try:
            resource = Resource.objects.get(id=resource_id)
        except Resource.DoesNotExist:
            return Response({'error': 'Resource not found'}, status=status.HTTP_404_NOT_FOUND)

        if action == 'approve':
            # Resource stays in DB (already published)
            return Response({'status': 'Resource approved'})
        elif action == 'reject':
            resource.delete()
            return Response({'status': 'Resource rejected and removed'})
        elif action == 'delete':
            resource.delete()
            return Response({'status': 'Resource deleted'})

        return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)


# ═══════════════════════════════════════════════════════════════
# MODULE 4 — GLOBAL NOTIFICATIONS
# ═══════════════════════════════════════════════════════════════

class BroadcastNotificationView(APIView):
    """Send notification to all users or a segment."""
    permission_classes = [IsSuperAdmin]

    def post(self, request):
        message = request.data.get('message', '')
        target = request.data.get('target', 'all')  # all, active, staff

        if not message:
            return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)

        if target == 'active':
            # Users active in last 7 days
            active_ids = (
                UserActivity.objects
                .filter(created_at__gte=timezone.now() - timedelta(days=7))
                .values_list('user_id', flat=True)
                .distinct()
            )
            users = User.objects.filter(id__in=active_ids)
        elif target == 'staff':
            users = User.objects.filter(is_staff=True)
        else:
            users = User.objects.filter(is_active=True)

        # Bulk create notifications
        notifications = [
            Notification(user=u, message=message)
            for u in users
        ]
        Notification.objects.bulk_create(notifications)

        return Response({
            'status': 'Notification sent',
            'recipients': len(notifications),
            'message': message,
        })

    def get(self, request):
        """Get recent broadcast history."""
        # Get unique messages sent in last 30 days
        recent = (
            Notification.objects
            .filter(created_at__gte=timezone.now() - timedelta(days=30))
            .values('message')
            .annotate(
                count=Count('id'),
                sent_at=Avg('created_at')  # approximate
            )
            .order_by('-sent_at')[:20]
        )
        return Response({'history': list(recent)})
