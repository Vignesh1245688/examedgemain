"""
Spaced Repetition Engine
Implements the SM-2 algorithm for optimal review scheduling.
Topics frequently forgotten reappear at scientifically optimal intervals.
"""
from django.utils import timezone
from datetime import timedelta
import math


class SpacedRepetitionEngine:
    """SM-2 based spaced repetition system for long-term knowledge retention."""

    def __init__(self, user):
        self.user = user

    def process_review(self, topic_name, quality_rating, subject=''):
        """
        Process a review and schedule the next one using SM-2 algorithm.
        
        quality_rating: 0-5
            0 - Complete blackout
            1 - Incorrect, but upon seeing correct answer, remembered
            2 - Incorrect, but correct answer seemed easy to recall
            3 - Correct, but with serious difficulty
            4 - Correct, after some hesitation
            5 - Perfect response
        """
        from recommendations.models import TopicMastery, RevisionSchedule

        mastery, created = TopicMastery.objects.get_or_create(
            user=self.user,
            topic_name=topic_name,
            defaults={'subject': subject}
        )

        # SM-2 Algorithm
        ef = mastery.easiness_factor
        rep = mastery.repetition_count

        if quality_rating >= 3:
            # Correct response
            if rep == 0:
                interval = 1
            elif rep == 1:
                interval = 6
            else:
                interval = int(mastery.repetition_interval * ef)

            rep += 1
        else:
            # Incorrect response — reset
            rep = 0
            interval = 1

        # Update easiness factor
        ef = ef + (0.1 - (5 - quality_rating) * (0.08 + (5 - quality_rating) * 0.02))
        ef = max(1.3, ef)  # Minimum EF is 1.3

        # Update mastery
        mastery.easiness_factor = ef
        mastery.repetition_count = rep
        mastery.repetition_interval = interval
        mastery.next_review_date = timezone.now() + timedelta(days=interval)
        mastery.last_practiced = timezone.now()
        mastery.save()

        # Create revision schedule entry
        RevisionSchedule.objects.create(
            user=self.user,
            topic=topic_name,
            subject=subject,
            review_date=(timezone.now() + timedelta(days=interval)).date(),
            interval_days=interval,
            repetition_number=rep,
            performance_rating=quality_rating,
        )

        return {
            'topic': topic_name,
            'next_review': mastery.next_review_date.isoformat(),
            'interval_days': interval,
            'easiness_factor': round(ef, 2),
            'repetition_count': rep,
        }

    def get_due_reviews(self, limit=10):
        """Get topics due for review today."""
        from recommendations.models import TopicMastery, RevisionSchedule

        today = timezone.now().date()

        # From TopicMastery
        due_topics = TopicMastery.objects.filter(
            user=self.user,
            next_review_date__lte=timezone.now(),
        ).order_by('next_review_date')[:limit]

        reviews = []
        for mastery in due_topics:
            overdue_days = (today - mastery.next_review_date.date()).days if mastery.next_review_date else 0
            reviews.append({
                'topic': mastery.topic_name,
                'subject': mastery.subject,
                'accuracy': round(mastery.accuracy_percentage, 1),
                'mastery_level': mastery.mastery_level,
                'overdue_days': max(0, overdue_days),
                'repetition_count': mastery.repetition_count,
                'priority': 'high' if overdue_days > 3 else 'medium' if overdue_days > 0 else 'normal',
            })

        # Sort by overdue days (most overdue first)
        reviews.sort(key=lambda x: -x['overdue_days'])
        return reviews

    def get_revision_stats(self):
        """Get revision statistics for the user."""
        from recommendations.models import RevisionSchedule, TopicMastery

        today = timezone.now().date()

        total_reviews = RevisionSchedule.objects.filter(user=self.user).count()
        completed_reviews = RevisionSchedule.objects.filter(
            user=self.user, is_completed=True
        ).count()
        due_today = TopicMastery.objects.filter(
            user=self.user,
            next_review_date__date__lte=today,
        ).count()
        upcoming_week = TopicMastery.objects.filter(
            user=self.user,
            next_review_date__date__gt=today,
            next_review_date__date__lte=today + timedelta(days=7),
        ).count()

        return {
            'total_reviews': total_reviews,
            'completed_reviews': completed_reviews,
            'due_today': due_today,
            'upcoming_week': upcoming_week,
            'completion_rate': round(
                (completed_reviews / total_reviews * 100) if total_reviews > 0 else 0, 1
            ),
        }

    def auto_schedule_weak_topics(self):
        """Automatically schedule reviews for weak topics that don't have schedules."""
        from recommendations.models import TopicMastery

        weak_topics = TopicMastery.objects.filter(
            user=self.user,
            is_weak=True,
            next_review_date__isnull=True,
        )

        scheduled = []
        for mastery in weak_topics:
            mastery.next_review_date = timezone.now() + timedelta(days=1)
            mastery.repetition_interval = 1
            mastery.save()
            scheduled.append(mastery.topic_name)

        return scheduled
