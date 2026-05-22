"""
Daily Task Generator
Generates AI-based daily study tasks based on weak topics, exam goals, and activity history.
"""
from django.utils import timezone
from datetime import timedelta


class DailyTaskGenerator:
    def __init__(self, user):
        self.user = user

    def generate_tasks(self, date=None):
        from recommendations.models import DailyTask, TopicMastery, UserLearningProfile, LearningStreak
        target_date = date or timezone.now().date()

        existing = DailyTask.objects.filter(user=self.user, date=target_date)
        if existing.exists():
            return list(existing)

        tasks_data = []
        weak = list(TopicMastery.objects.filter(user=self.user, is_weak=True).order_by('accuracy_percentage')[:3])
        improving = list(TopicMastery.objects.filter(user=self.user, is_improving=True).order_by('-accuracy_percentage')[:2])

        order = 0
        # Task 1: Weak topic quiz
        if weak:
            t = weak[0]
            order += 1
            tasks_data.append({
                'task_type': 'quiz', 'title': f'Practice {t.topic_name} Quiz',
                'description': f'Your accuracy is {t.accuracy_percentage:.0f}%. Let\'s improve it!',
                'topic': t.topic_name, 'subject': t.subject, 'difficulty': 'easy' if t.accuracy_percentage < 30 else 'medium',
                'xp_reward': 15, 'order': order,
            })

        # Task 2: Revision
        if len(weak) > 1:
            t = weak[1]
            order += 1
            tasks_data.append({
                'task_type': 'revision', 'title': f'Revise {t.topic_name} Notes',
                'description': f'Review key concepts to strengthen your understanding.',
                'topic': t.topic_name, 'subject': t.subject, 'difficulty': 'easy',
                'xp_reward': 10, 'order': order,
            })

        # Task 3: Advanced practice for improving topics
        if improving:
            t = improving[0]
            order += 1
            tasks_data.append({
                'task_type': 'practice', 'title': f'{t.topic_name} — Level Up!',
                'description': f'You\'re improving! Try harder questions.',
                'topic': t.topic_name, 'subject': t.subject, 'difficulty': 'hard',
                'xp_reward': 20, 'order': order,
            })

        # Task 4: Flashcard review
        order += 1
        topic_name = weak[2].topic_name if len(weak) > 2 else (weak[0].topic_name if weak else 'General Studies')
        tasks_data.append({
            'task_type': 'flashcard', 'title': f'Review {topic_name} Flashcards',
            'description': 'Quick recall session to reinforce memory.',
            'topic': topic_name, 'difficulty': 'easy', 'xp_reward': 10, 'order': order,
        })

        # Task 5: Mock test (every 3rd day)
        day_of_year = target_date.timetuple().tm_yday
        if day_of_year % 3 == 0:
            order += 1
            tasks_data.append({
                'task_type': 'mock_test', 'title': 'Daily Mini Mock Test',
                'description': 'A timed 10-question mixed test.', 'difficulty': 'medium',
                'xp_reward': 25, 'order': order,
            })

        # Fallback if no data
        if not tasks_data:
            tasks_data = [
                {'task_type': 'quiz', 'title': 'Explore a Practice Quiz', 'description': 'Start with any topic.', 'difficulty': 'easy', 'xp_reward': 10, 'order': 1},
                {'task_type': 'reading', 'title': 'Browse Study Resources', 'description': 'Find PDFs and videos.', 'difficulty': 'easy', 'xp_reward': 5, 'order': 2},
                {'task_type': 'revision', 'title': 'Set Your Target Exam', 'description': 'Update your profile.', 'difficulty': 'easy', 'xp_reward': 5, 'order': 3},
            ]

        created = []
        for td in tasks_data:
            task = DailyTask.objects.create(user=self.user, date=target_date, **td)
            created.append(task)
        return created

    def complete_task(self, task_id):
        from recommendations.models import DailyTask, LearningStreak
        try:
            task = DailyTask.objects.get(id=task_id, user=self.user)
            if not task.is_completed:
                task.is_completed = True
                task.completed_at = timezone.now()
                task.save()
                streak, _ = LearningStreak.objects.get_or_create(user=self.user)
                streak.record_activity(task.xp_reward)
            return task
        except DailyTask.DoesNotExist:
            return None

    def get_completion_stats(self, date=None):
        from recommendations.models import DailyTask
        target_date = date or timezone.now().date()
        tasks = DailyTask.objects.filter(user=self.user, date=target_date)
        total = tasks.count()
        completed = tasks.filter(is_completed=True).count()
        xp = sum(t.xp_reward for t in tasks.filter(is_completed=True))
        return {'total': total, 'completed': completed, 'percentage': round(completed / total * 100 if total else 0), 'xp_earned': xp}
