"""
AI Study Roadmap Generator
Creates personalized day-wise study plans.
"""
from django.utils import timezone
from datetime import timedelta, date


class RoadmapGenerator:
    EXAM_SUBJECTS = {
        'UPSC': ['History', 'Geography', 'Polity', 'Economy', 'Current Affairs', 'General Science'],
        'SSC': ['Quantitative Aptitude', 'English', 'General Awareness', 'Reasoning'],
        'Banking': ['Quantitative Aptitude', 'English', 'Reasoning', 'General Awareness'],
        'TNPSC': ['Tamil', 'History', 'Geography', 'Polity', 'Economy', 'Current Affairs', 'Aptitude'],
        'default': ['General Studies', 'Aptitude', 'Reasoning', 'Current Affairs'],
    }

    def __init__(self, user):
        self.user = user

    def generate_plan(self, target_exam, exam_date, study_hours_per_day=2.0, weak_subjects=None, patterns="", topics_to_cover=None, marks_allotted=None):
        from recommendations.models import StudyPlan, StudyPlanDay, TopicMastery
        today = timezone.now().date()
        if isinstance(exam_date, str):
            exam_date = date.fromisoformat(exam_date)
        total_days = max((exam_date - today).days, 30)
        
        # Use user-provided topics if available, else fallback to predefined subjects
        if topics_to_cover and len(topics_to_cover) > 0:
            subjects = topics_to_cover
        else:
            subjects = self._get_subjects(target_exam)
            
        weak_from_data = list(TopicMastery.objects.filter(user=self.user, is_weak=True).values_list('topic_name', flat=True))
        all_weak = list(set((weak_subjects or []) + weak_from_data))

        plan = StudyPlan.objects.create(
            user=self.user, title=f'{target_exam} Plan — {total_days} Days',
            target_exam=target_exam, exam_date=exam_date, start_date=today,
            study_hours_per_day=study_hours_per_day, weak_subjects=all_weak, total_days=total_days,
            patterns=patterns, topics_to_cover=topics_to_cover or [], marks_allotted=marks_allotted or {}
        )
        self._generate_days(plan, subjects, all_weak, total_days, study_hours_per_day)
        plan.update_progress()
        return plan

    def _get_subjects(self, exam_name):
        for key, subs in self.EXAM_SUBJECTS.items():
            if key in exam_name.upper():
                return subs
        return self.EXAM_SUBJECTS['default']

    def _generate_days(self, plan, subjects, weak, total_days, hours):
        from recommendations.models import StudyPlanDay
        cycle = []
        for s in subjects:
            cycle.append(s)
            if s.lower() in [w.lower() for w in weak]:
                cycle.append(s)
        cycle = cycle or ['General Studies']
        minutes = int(hours * 60)

        for d in range(1, total_days + 1):
            dt = plan.start_date + timedelta(days=d - 1)
            is_rev = d % 7 == 0
            is_mock = d > 10 and d % 10 == 0
            focus = cycle[(d - 1) % len(cycle)]

            if d <= total_days * 0.5:
                phase = 'Learning'
            elif d <= total_days * 0.8:
                phase = 'Practice'
            else:
                phase = 'Revision'
                is_mock = is_mock or d % 3 == 0

            tasks = []
            if is_mock:
                tasks = [{'type': 'mock_test', 'title': f'Mock Test — {focus}', 'topic': focus, 'duration_minutes': min(90, minutes), 'completed': False},
                         {'type': 'revision', 'title': f'Review mistakes', 'topic': focus, 'duration_minutes': max(minutes - 90, 30), 'completed': False}]
                title = f'📝 Mock Test: {focus}'
            elif is_rev:
                tasks = [{'type': 'revision', 'title': f'Revise {focus}', 'topic': focus, 'duration_minutes': int(minutes * 0.6), 'completed': False},
                         {'type': 'quiz', 'title': f'Quick quiz — {focus}', 'topic': focus, 'duration_minutes': int(minutes * 0.4), 'completed': False}]
                title = f'🔄 Revision: {focus}'
            else:
                tasks = [{'type': 'reading', 'title': f'Study {focus}', 'topic': focus, 'duration_minutes': int(minutes * 0.5), 'completed': False},
                         {'type': 'quiz', 'title': f'Practice — {focus}', 'topic': focus, 'duration_minutes': int(minutes * 0.3), 'completed': False},
                         {'type': 'flashcard', 'title': f'Flashcards — {focus}', 'topic': focus, 'duration_minutes': int(minutes * 0.2), 'completed': False}]
                title = f'📖 {phase}: {focus}'

            StudyPlanDay.objects.create(plan=plan, day_number=d, date=dt, title=title, tasks=tasks,
                                        focus_topics=[focus], study_hours=hours, is_revision_day=is_rev, is_mock_test_day=is_mock)

    def get_active_plan(self):
        from recommendations.models import StudyPlan
        return StudyPlan.objects.filter(user=self.user, is_active=True).order_by('-created_at').first()

    def mark_day_complete(self, plan_id, day_number):
        from recommendations.models import StudyPlan, StudyPlanDay
        try:
            plan = StudyPlan.objects.get(id=plan_id, user=self.user)
            day = plan.days.get(day_number=day_number)
            day.is_completed = True
            day.completed_at = timezone.now()
            day.save()
            plan.update_progress()
            return True
        except (StudyPlan.DoesNotExist, StudyPlanDay.DoesNotExist):
            return False
