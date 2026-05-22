"""
Adaptive Learning Engine
Handles difficulty progression: Easy → Medium → Hard
Adjusts recommendations based on user improvement patterns.
"""
from django.utils import timezone


class AdaptiveEngine:
    """Manages adaptive difficulty progression for personalized learning."""

    DIFFICULTY_LEVELS = ['easy', 'medium', 'hard']

    # Thresholds for difficulty transitions
    PROMOTE_THRESHOLD = 75.0    # Accuracy to move up
    DEMOTE_THRESHOLD = 35.0     # Accuracy to move down
    MIN_ATTEMPTS_TO_CHANGE = 5  # Minimum attempts before changing difficulty

    def __init__(self, user):
        self.user = user

    def evaluate_and_adapt(self, topic_name=None):
        """Evaluate all or specific topic mastery and adapt difficulty."""
        from recommendations.models import TopicMastery, UserLearningProfile

        filters = {'user': self.user}
        if topic_name:
            filters['topic_name'] = topic_name

        masteries = TopicMastery.objects.filter(**filters)
        adaptations = []

        for mastery in masteries:
            if mastery.total_attempts < self.MIN_ATTEMPTS_TO_CHANGE:
                continue

            old_difficulty = mastery.difficulty_level
            new_difficulty = self._calculate_difficulty(mastery)

            if new_difficulty != old_difficulty:
                mastery.difficulty_level = new_difficulty
                mastery.save()
                adaptations.append({
                    'topic': mastery.topic_name,
                    'old_difficulty': old_difficulty,
                    'new_difficulty': new_difficulty,
                    'accuracy': mastery.accuracy_percentage,
                    'direction': 'up' if self.DIFFICULTY_LEVELS.index(new_difficulty) > self.DIFFICULTY_LEVELS.index(old_difficulty) else 'down',
                })

        # Update global difficulty level
        self._update_global_difficulty()

        return adaptations

    def _calculate_difficulty(self, mastery):
        """Calculate appropriate difficulty based on performance trends."""
        accuracy = mastery.accuracy_percentage
        recent_scores = mastery.recent_scores or []
        current = mastery.difficulty_level

        # Check recent trend (last 5 attempts)
        if len(recent_scores) >= 3:
            recent_avg = sum(recent_scores[-3:]) / 3
        else:
            recent_avg = accuracy

        current_idx = self.DIFFICULTY_LEVELS.index(current)

        # Promote: consistently high accuracy
        if recent_avg >= self.PROMOTE_THRESHOLD and current_idx < 2:
            # Extra check: at least 3 of last 5 scores above threshold
            if len(recent_scores) >= 3:
                above = sum(1 for s in recent_scores[-5:] if s >= self.PROMOTE_THRESHOLD)
                if above >= 3:
                    return self.DIFFICULTY_LEVELS[current_idx + 1]

        # Demote: consistently struggling
        if recent_avg <= self.DEMOTE_THRESHOLD and current_idx > 0:
            if len(recent_scores) >= 3:
                below = sum(1 for s in recent_scores[-5:] if s <= self.DEMOTE_THRESHOLD)
                if below >= 3:
                    return self.DIFFICULTY_LEVELS[current_idx - 1]

        return current

    def _update_global_difficulty(self):
        """Update the user's global difficulty level based on overall performance."""
        from recommendations.models import TopicMastery, UserLearningProfile

        masteries = TopicMastery.objects.filter(
            user=self.user, total_attempts__gte=self.MIN_ATTEMPTS_TO_CHANGE
        )

        if not masteries.exists():
            return

        avg_accuracy = sum(m.accuracy_percentage for m in masteries) / masteries.count()

        if avg_accuracy >= 80:
            global_level = 'advanced'
        elif avg_accuracy >= 50:
            global_level = 'intermediate'
        else:
            global_level = 'beginner'

        profile, _ = UserLearningProfile.objects.get_or_create(user=self.user)
        if profile.current_difficulty_level != global_level:
            profile.current_difficulty_level = global_level
            profile.save()

    def get_recommended_difficulty(self, topic_name):
        """Get the recommended difficulty for a specific topic."""
        from recommendations.models import TopicMastery

        try:
            mastery = TopicMastery.objects.get(user=self.user, topic_name=topic_name)
            return mastery.difficulty_level
        except TopicMastery.DoesNotExist:
            # Check global level
            try:
                from recommendations.models import UserLearningProfile
                profile = UserLearningProfile.objects.get(user=self.user)
                level_map = {
                    'beginner': 'easy',
                    'intermediate': 'medium',
                    'advanced': 'hard',
                }
                return level_map.get(profile.current_difficulty_level, 'medium')
            except UserLearningProfile.DoesNotExist:
                return 'medium'

    def get_progression_status(self):
        """Get overall learning progression summary."""
        from recommendations.models import TopicMastery, UserLearningProfile

        masteries = TopicMastery.objects.filter(user=self.user)

        difficulty_counts = {'easy': 0, 'medium': 0, 'hard': 0}
        mastery_counts = {'novice': 0, 'learning': 0, 'proficient': 0, 'expert': 0}

        for m in masteries:
            difficulty_counts[m.difficulty_level] = difficulty_counts.get(m.difficulty_level, 0) + 1
            mastery_counts[m.mastery_level] = mastery_counts.get(m.mastery_level, 0) + 1

        total = masteries.count() or 1
        avg_accuracy = sum(m.accuracy_percentage for m in masteries) / total if masteries.exists() else 0

        try:
            profile = UserLearningProfile.objects.get(user=self.user)
            global_level = profile.current_difficulty_level
        except UserLearningProfile.DoesNotExist:
            global_level = 'intermediate'

        return {
            'global_difficulty': global_level,
            'average_accuracy': round(avg_accuracy, 1),
            'total_topics': total,
            'difficulty_distribution': difficulty_counts,
            'mastery_distribution': mastery_counts,
            'topics_at_expert': mastery_counts.get('expert', 0),
            'topics_improving': TopicMastery.objects.filter(user=self.user, is_improving=True).count(),
        }
