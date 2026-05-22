from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta

from .models import (
    UserLearningProfile, TopicMastery, UserActivity,
    Recommendation, DailyTask, StudyPlan, StudyPlanDay,
    RevisionSchedule, LearningStreak, DailyRevisionQuestion
)
from .serializers import (
    UserLearningProfileSerializer, TopicMasterySerializer,
    UserActivitySerializer, RecommendationSerializer,
    DailyTaskSerializer, StudyPlanSerializer, StudyPlanCreateSerializer,
    RevisionScheduleSerializer, LearningStreakSerializer
)
from .services import (
    RecommendationEngine, WeakTopicDetector, AdaptiveEngine,
    SpacedRepetitionEngine, RoadmapGenerator, DailyTaskGenerator
)


class PersonalizedFeedView(APIView):
    """AI-powered personalized resource feed."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        engine = RecommendationEngine(request.user)
        
        # Check for fresh recommendations of the NEW types
        recent = Recommendation.objects.filter(
            user=request.user, is_completed=False, is_dismissed=False,
            reason__in=['trending', 'weak_topic_resource'],
            created_at__gte=timezone.now() - timedelta(hours=6)
        )
        
        if recent.count() < 5:
            # Delete old recommendations that don't match the new system
            Recommendation.objects.filter(user=request.user).exclude(reason__in=['trending', 'weak_topic_resource']).delete()
            engine.generate_feed(limit=20)
            recent = Recommendation.objects.filter(
                user=request.user, is_completed=False, is_dismissed=False,
                reason__in=['trending', 'weak_topic_resource']
            ).order_by('-final_score')

        serializer = RecommendationSerializer(recent[:20], many=True, context={'request': request})
        return Response({
            'feed': serializer.data,
            'generated_at': timezone.now().isoformat(),
            'total_count': recent.count(),
        })


class UpNextCarouselView(APIView):
    """'Up Next For You' carousel recommendations."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        engine = RecommendationEngine(request.user)
        items = engine.get_up_next(limit=8)
        serializer = RecommendationSerializer(items, many=True, context={'request': request})
        return Response({'items': serializer.data})


class WeakTopicsView(APIView):
    """Weak topic detection and analysis."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        detector = WeakTopicDetector(request.user)
        analysis = detector.analyze()
        return Response(analysis)


class DailyTasksView(APIView):
    """AI-generated daily study tasks."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        generator = DailyTaskGenerator(request.user)
        tasks = generator.generate_tasks()
        stats = generator.get_completion_stats()
        serializer = DailyTaskSerializer(tasks, many=True)
        return Response({'tasks': serializer.data, 'stats': stats})

    def post(self, request):
        """Complete a task."""
        task_id = request.data.get('task_id')
        if not task_id:
            return Response({'error': 'task_id required'}, status=status.HTTP_400_BAD_REQUEST)
        generator = DailyTaskGenerator(request.user)
        task = generator.complete_task(task_id)
        if task:
            return Response(DailyTaskSerializer(task).data)
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)


class StudyPlanView(APIView):
    """AI study roadmap generation and management."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        plan_id = request.query_params.get('id')
        if plan_id:
            try:
                plan = StudyPlan.objects.get(id=plan_id, user=request.user)
                serializer = StudyPlanSerializer(plan)
                return Response(serializer.data)
            except StudyPlan.DoesNotExist:
                return Response({'error': 'Plan not found'}, status=status.HTTP_404_NOT_FOUND)
        
        plans = StudyPlan.objects.filter(user=request.user).order_by('-created_at')
        # Don't include days in list view for performance
        data = []
        for plan in plans[:10]:
            data.append({
                'id': plan.id, 'title': plan.title, 'target_exam': plan.target_exam,
                'exam_date': plan.exam_date, 'start_date': plan.start_date,
                'progress_percentage': plan.progress_percentage,
                'total_days': plan.total_days, 'completed_days': plan.completed_days,
                'is_active': plan.is_active, 'created_at': plan.created_at,
            })
        return Response({'plans': data})

    def post(self, request):
        serializer = StudyPlanCreateSerializer(data=request.data)
        if serializer.is_valid():
            generator = RoadmapGenerator(request.user)
            plan = generator.generate_plan(**serializer.validated_data)
            return Response(StudyPlanSerializer(plan).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudyPlanDayCompleteView(APIView):
    """Mark a study plan day as complete."""
    permission_classes = [IsAuthenticated]

    def post(self, request, plan_id, day_number):
        generator = RoadmapGenerator(request.user)
        success = generator.mark_day_complete(plan_id, day_number)
        if success:
            # Award XP
            streak, _ = LearningStreak.objects.get_or_create(user=request.user)
            streak.record_activity(xp_earned=20)
            return Response({'status': 'completed', 'xp_earned': 20})
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)


class AdvancedAnalyticsView(APIView):
    """Advanced AI analytics dashboard data."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        detector = WeakTopicDetector(user)
        adaptive = AdaptiveEngine(user)
        sr = SpacedRepetitionEngine(user)

        weak_analysis = detector.analyze()
        progression = adaptive.get_progression_status()
        revision_stats = sr.get_revision_stats()

        # Activity heatmap (last 30 days)
        activities = UserActivity.objects.filter(
            user=user, created_at__gte=timezone.now() - timedelta(days=30)
        )
        heatmap = {}
        for act in activities:
            day = act.created_at.date().isoformat()
            heatmap[day] = heatmap.get(day, 0) + 1

        # Topic mastery for charts
        masteries = TopicMastery.objects.filter(user=user).order_by('-accuracy_percentage')
        topic_chart = [
            {'topic': m.topic_name, 'accuracy': round(m.accuracy_percentage, 1),
             'attempts': m.total_attempts, 'mastery': m.mastery_level, 'is_weak': m.is_weak}
            for m in masteries[:15]
        ]

        # Streak data
        try:
            streak = LearningStreak.objects.get(user=user)
            streak_data = LearningStreakSerializer(streak).data
        except LearningStreak.DoesNotExist:
            streak_data = {'current_streak': 0, 'longest_streak': 0, 'total_xp': 0, 'level': 1}

        # Daily task completion
        task_gen = DailyTaskGenerator(user)
        task_stats = task_gen.get_completion_stats()

        return Response({
            'weak_topics': weak_analysis['weak_topics'][:5],
            'strong_topics': weak_analysis['strong_topics'][:5],
            'improving_topics': weak_analysis['improving_topics'][:5],
            'suggestions': weak_analysis['suggestions'][:5],
            'summary': weak_analysis['summary'],
            'progression': progression,
            'revision_stats': revision_stats,
            'activity_heatmap': heatmap,
            'topic_chart': topic_chart,
            'streak': streak_data,
            'daily_tasks': task_stats,
        })


class LearningProfileView(APIView):
    """User learning preferences management."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, created = UserLearningProfile.objects.get_or_create(user=request.user)
        return Response(UserLearningProfileSerializer(profile).data)

    def put(self, request):
        profile, created = UserLearningProfile.objects.get_or_create(user=request.user)
        serializer = UserLearningProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RevisionQueueView(APIView):
    """Spaced repetition review queue."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sr = SpacedRepetitionEngine(request.user)
        due = sr.get_due_reviews(limit=10)
        stats = sr.get_revision_stats()
        return Response({'due_reviews': due, 'stats': stats})

    def post(self, request):
        """Process a review completion."""
        topic = request.data.get('topic')
        rating = request.data.get('rating', 3)
        if not topic:
            return Response({'error': 'topic required'}, status=status.HTTP_400_BAD_REQUEST)
        sr = SpacedRepetitionEngine(request.user)
        result = sr.process_review(topic, int(rating))
        return Response(result)


class StreakView(APIView):
    """Streak and gamification data."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        streak, _ = LearningStreak.objects.get_or_create(user=request.user)
        return Response(LearningStreakSerializer(streak).data)


class TrackActivityView(APIView):
    """Track user learning activity."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = UserActivitySerializer(data=request.data)
        if serializer.is_valid():
            activity = serializer.save(user=request.user)
            # Update streak
            streak, _ = LearningStreak.objects.get_or_create(user=request.user)
            streak.record_activity(xp_earned=5)
            # Update topic mastery if quiz
            if activity.activity_type == 'quiz_attempt' and activity.topic:
                detector = WeakTopicDetector(request.user)
                detector.update_topic_from_quiz(
                    activity.topic,
                    correct=int(activity.score or 0),
                    total=int(activity.max_score or 1),
                    time_seconds=activity.time_spent_seconds,
                    subject=activity.subject,
                )
            return Response(UserActivitySerializer(activity).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RecommendationActionView(APIView):
    """Dismiss or complete a recommendation."""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        action = request.data.get('action', 'complete')
        try:
            rec = Recommendation.objects.get(id=pk, user=request.user)
            if action == 'dismiss':
                rec.is_dismissed = True
            else:
                rec.is_completed = True
            rec.save()
            return Response({'status': 'ok'})
        except Recommendation.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)


class DailyRevisionView(APIView):
    """Daily Revision Quiz — collects all wrongly-answered questions from today
    and compiles them into a single revision quiz."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get today's revision quiz (all wrong answers from today)."""
        today = timezone.now().date()
        questions = DailyRevisionQuestion.objects.filter(
            user=request.user, date=today
        ).order_by('created_at')

        total = questions.count()
        unrevised = questions.filter(is_revised=False).count()
        revised = questions.filter(is_revised=True).count()
        revised_correctly = questions.filter(revised_correctly=True).count()

        quiz_questions = []
        for q in questions.filter(is_revised=False):
            item = {
                'id': q.id,
                'question': q.question_text,
                'type': q.question_type,
                'options': q.options if q.options else [],
                'correctAnswer': q.correct_answer,
                'explanation': q.explanation,
                'reference': q.reference,
                'topic': q.topic,
                'difficulty': q.difficulty,
                'original_wrong_answer': q.user_answer,
                'source_quiz': q.source_quiz_title,
            }
            quiz_questions.append(item)

        # Timer: 45 sec per MCQ, 30 sec per T/F, 60 sec for others
        timer = 0
        for q in quiz_questions:
            if q['type'] == 'mcq': timer += 45
            elif q['type'] == 'true_false': timer += 30
            else: timer += 60

        return Response({
            'questions': quiz_questions,
            'stats': {
                'total_wrong_today': total,
                'unrevised': unrevised,
                'revised': revised,
                'revised_correctly': revised_correctly,
                'accuracy': round((revised_correctly / revised * 100) if revised > 0 else 0, 1),
            },
            'recommended_timer': timer,
            'date': today.isoformat(),
        })

    def post(self, request):
        """Submit revision quiz results."""
        results = request.data.get('results', [])
        # results: [{id: question_id, user_answer: string, is_correct: bool}]
        if not results:
            return Response({'error': 'No results provided'}, status=status.HTTP_400_BAD_REQUEST)

        correct_count = 0
        total_count = 0
        for r in results:
            try:
                q = DailyRevisionQuestion.objects.get(id=r['id'], user=request.user)
                q.is_revised = True
                q.revised_correctly = r.get('is_correct', False)
                q.revised_at = timezone.now()
                q.user_answer = str(r.get('user_answer', ''))
                q.save()
                total_count += 1
                if q.revised_correctly:
                    correct_count += 1
            except DailyRevisionQuestion.DoesNotExist:
                continue

        # Award XP for revision
        try:
            streak, _ = LearningStreak.objects.get_or_create(user=request.user)
            xp = 10 + (correct_count * 3)  # bonus XP per correct revision
            streak.record_activity(xp_earned=xp)
        except Exception:
            xp = 0

        return Response({
            'status': 'ok',
            'total_revised': total_count,
            'correct': correct_count,
            'accuracy': round((correct_count / total_count * 100) if total_count > 0 else 0, 1),
            'xp_earned': xp,
        })


class LeaderboardView(APIView):
    """Get the top 10 users by weekly XP for the gamification leaderboard."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        streaks = LearningStreak.objects.select_related('user').order_by('-weekly_xp')[:10]
        
        leaderboard = []
        for index, streak in enumerate(streaks):
            # Use first name if available, otherwise username
            name = streak.user.first_name if streak.user.first_name else streak.user.username
            
            leaderboard.append({
                'rank': index + 1,
                'username': streak.user.username,
                'display_name': name,
                'weekly_xp': streak.weekly_xp,
                'level': streak.level,
                'is_current_user': streak.user.id == request.user.id
            })
            
        return Response({'leaderboard': leaderboard}, status=status.HTTP_200_OK)
