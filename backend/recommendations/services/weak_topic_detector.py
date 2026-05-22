"""
Weak Topic Detection Engine
Analyzes user performance data to identify weak topics,
repeated mistakes, low accuracy areas, and slow response topics.
"""
from django.utils import timezone
from django.db.models import Avg, Count, Sum
from datetime import timedelta


class WeakTopicDetector:
    """AI engine that detects weak subjects, repeated mistakes,
    low accuracy topics, and slow response areas."""

    WEAK_THRESHOLD = 50.0       # Below 50% accuracy = weak
    STRONG_THRESHOLD = 75.0     # Above 75% = strong
    MIN_ATTEMPTS = 3            # Minimum attempts before classification
    SLOW_RESPONSE_MULTIPLIER = 1.5  # 1.5x average = slow

    def __init__(self, user):
        self.user = user

    def analyze(self):
        """Run full weak topic analysis and return comprehensive results."""
        from recommendations.models import TopicMastery, UserActivity

        masteries = TopicMastery.objects.filter(user=self.user)

        if not masteries.exists():
            # Bootstrap from practice quiz results
            self._bootstrap_from_quiz_results()
            masteries = TopicMastery.objects.filter(user=self.user)

        weak_topics = []
        strong_topics = []
        improving_topics = []
        declining_topics = []
        all_topics = []

        for m in masteries:
            topic_data = {
                'topic': m.topic_name,
                'subject': m.subject,
                'accuracy': round(m.accuracy_percentage, 1),
                'attempts': m.total_attempts,
                'mastery_level': m.mastery_level,
                'confidence': round(m.confidence_score, 1),
                'avg_time': round(m.avg_time_per_question, 1),
                'is_improving': m.is_improving,
                'recent_trend': self._calculate_trend(m.recent_scores),
            }
            all_topics.append(topic_data)

            if m.total_attempts >= self.MIN_ATTEMPTS:
                if m.accuracy_percentage < self.WEAK_THRESHOLD:
                    weak_topics.append(topic_data)
                elif m.accuracy_percentage >= self.STRONG_THRESHOLD:
                    strong_topics.append(topic_data)

                if m.is_improving:
                    improving_topics.append(topic_data)
                elif len(m.recent_scores) >= 3:
                    recent = m.recent_scores[-3:]
                    if recent[-1] < recent[0]:
                        declining_topics.append(topic_data)

        # --- Topic Generalization Logic ---
        # Group weak topics by their parent subject
        subject_groups = {}
        for wt in weak_topics:
            subj = wt.get('subject')
            if subj and subj.strip():  # Only group if subject is defined
                if subj not in subject_groups:
                    subject_groups[subj] = []
                subject_groups[subj].append(wt)
        
        # If a subject has 3 or more weak subtopics, replace them with a generalized subject topic
        GENERALIZATION_THRESHOLD = 3
        generalized_weak_topics = []
        topics_to_remove = set()
        
        for subj, topics in subject_groups.items():
            if len(topics) >= GENERALIZATION_THRESHOLD:
                # Calculate average accuracy across these weak subtopics
                avg_accuracy = sum(t['accuracy'] for t in topics) / len(topics)
                total_attempts = sum(t['attempts'] for t in topics)
                
                # Create a generalized topic
                generalized_weak_topics.append({
                    'topic': subj,  # The parent subject becomes the main topic
                    'subject': subj,
                    'accuracy': round(avg_accuracy, 1),
                    'attempts': total_attempts,
                    'mastery_level': 'novice',
                    'confidence': sum(t.get('confidence', 50) for t in topics) / len(topics),
                    'avg_time': sum(t.get('avg_time', 0) for t in topics) / len(topics),
                    'is_improving': any(t.get('is_improving', False) for t in topics),
                    'recent_trend': 'declining',
                    'is_generalized': True,
                    'generalized_from': [t['topic'] for t in topics] # e.g., ['Planets', 'Satellites', 'Meteoroids']
                })
                
                # Mark original subtopics for removal
                for t in topics:
                    # Using topic name to track removal
                    topics_to_remove.add(t['topic'])
        
        # Remove individual subtopics that were generalized
        filtered_weak_topics = [wt for wt in weak_topics if wt['topic'] not in topics_to_remove]
        
        # Combine remaining specific topics with the new generalized parent topics
        final_weak_topics = filtered_weak_topics + generalized_weak_topics

        # Sort weak topics by accuracy (worst first)
        final_weak_topics.sort(key=lambda x: x['accuracy'])
        strong_topics.sort(key=lambda x: -x['accuracy'])

        return {
            'weak_topics': weak_topics,
            'strong_topics': strong_topics,
            'improving_topics': improving_topics,
            'declining_topics': declining_topics,
            'all_topics': all_topics,
            'summary': self._generate_summary(weak_topics, strong_topics, improving_topics),
            'suggestions': self._generate_suggestions(weak_topics, declining_topics),
        }

    def _bootstrap_from_quiz_results(self):
        """Create TopicMastery entries from existing PracticeQuizResult data."""
        from practice_quiz.models import PracticeQuizResult
        from recommendations.models import TopicMastery

        results = PracticeQuizResult.objects.filter(user=self.user)

        topic_data = {}
        for result in results:
            # Extract from topics_accuracy JSON field
            if result.topics_accuracy:
                for topic, accuracy in result.topics_accuracy.items():
                    if topic not in topic_data:
                        topic_data[topic] = {'scores': [], 'attempts': 0}
                    topic_data[topic]['scores'].append(accuracy)
                    topic_data[topic]['attempts'] += 1

            # Extract from weak_topics JSON field
            if result.weak_topics:
                for topic in result.weak_topics:
                    if isinstance(topic, str) and topic not in topic_data:
                        topic_data[topic] = {'scores': [30.0], 'attempts': 1}

        for topic_name, data in topic_data.items():
            avg_accuracy = sum(data['scores']) / len(data['scores']) if data['scores'] else 0
            mastery, created = TopicMastery.objects.get_or_create(
                user=self.user,
                topic_name=topic_name,
                defaults={
                    'total_attempts': data['attempts'] * 3,  # estimate
                    'correct_answers': int(data['attempts'] * 3 * avg_accuracy / 100),
                    'accuracy_percentage': avg_accuracy,
                    'recent_scores': data['scores'][-10:],
                    'last_practiced': timezone.now(),
                }
            )
            if not created:
                mastery.recent_scores = (mastery.recent_scores or []) + data['scores']
                mastery.recent_scores = mastery.recent_scores[-10:]
            mastery.update_mastery()

    def _calculate_trend(self, scores):
        """Calculate trend direction from recent scores."""
        if not scores or len(scores) < 2:
            return 'stable'
        recent = scores[-5:]
        if len(recent) < 2:
            return 'stable'
        first_half = sum(recent[:len(recent)//2]) / max(len(recent)//2, 1)
        second_half = sum(recent[len(recent)//2:]) / max(len(recent) - len(recent)//2, 1)
        diff = second_half - first_half
        if diff > 5:
            return 'improving'
        elif diff < -5:
            return 'declining'
        return 'stable'

    def _generate_summary(self, weak, strong, improving):
        """Generate a human-readable performance summary."""
        parts = []
        if weak:
            topics = ', '.join([t['topic'] for t in weak[:3]])
            parts.append(f"You need to focus on: {topics}")
        if strong:
            topics = ', '.join([t['topic'] for t in strong[:3]])
            parts.append(f"You're strong in: {topics}")
        if improving:
            topics = ', '.join([t['topic'] for t in improving[:3]])
            parts.append(f"Great improvement in: {topics}")
        return ' | '.join(parts) if parts else 'Keep practicing to build your profile!'

    def _generate_suggestions(self, weak, declining):
        """Generate actionable improvement suggestions."""
        suggestions = []
        for topic in weak[:5]:
            suggestions.append({
                'topic': topic['topic'],
                'suggestion': f"Practice more {topic['topic']} questions. "
                              f"Current accuracy: {topic['accuracy']}%. "
                              f"Try starting with Easy difficulty.",
                'priority': 'high' if topic['accuracy'] < 30 else 'medium',
                'action': 'practice',
            })
        for topic in declining[:3]:
            suggestions.append({
                'topic': topic['topic'],
                'suggestion': f"Your {topic['topic']} scores are declining. "
                              f"Schedule a revision session.",
                'priority': 'medium',
                'action': 'revision',
            })
        return suggestions

    def update_topic_from_quiz(self, topic_name, correct, total, time_seconds, subject=''):
        """Update topic mastery after a quiz attempt."""
        from recommendations.models import TopicMastery

        mastery, created = TopicMastery.objects.get_or_create(
            user=self.user,
            topic_name=topic_name,
            defaults={'subject': subject}
        )

        mastery.total_attempts += total
        mastery.correct_answers += correct
        mastery.subject = subject or mastery.subject

        # Update time tracking
        if total > 0:
            new_avg_time = time_seconds / total
            if mastery.avg_time_per_question > 0:
                mastery.avg_time_per_question = (
                    mastery.avg_time_per_question * 0.7 + new_avg_time * 0.3
                )
            else:
                mastery.avg_time_per_question = new_avg_time

        # Update recent scores
        accuracy = (correct / total * 100) if total > 0 else 0
        scores = mastery.recent_scores or []
        scores.append(round(accuracy, 1))
        mastery.recent_scores = scores[-10:]

        # Update confidence (weighted moving average)
        mastery.confidence_score = (
            mastery.confidence_score * 0.6 + accuracy * 0.4
        )

        mastery.last_practiced = timezone.now()
        mastery.update_mastery()

        return mastery
