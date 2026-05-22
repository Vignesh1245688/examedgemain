"""
Recommendation Scoring Engine
Generates and ranks personalized recommendations using a multi-factor scoring algorithm.
"""
from django.utils import timezone
from django.db.models import Avg, Count, Q
from datetime import timedelta
import random


class RecommendationEngine:
    """Core AI engine that generates scored, ranked recommendations."""

    # Scoring weights
    WEIGHTS = {
        'weak_topic': 0.35,
        'user_interest': 0.15,
        'exam_relevance': 0.20,
        'trending': 0.05,
        'spaced_repetition': 0.20,
        'adaptive_difficulty': 0.05,
    }

    def __init__(self, user):
        self.user = user

    def generate_feed(self, limit=20):
        """Generate a personalized resource feed ranked by relevance."""
        from recommendations.models import Recommendation, TopicMastery
        from resources.models import Resource

        # Clear old recommendations (older than 24h)
        Recommendation.objects.filter(
            user=self.user,
            created_at__lt=timezone.now() - timedelta(hours=24)
        ).delete()

        recommendations = []

        # 1. Recommended based on weak topics (Higher personalization priority)
        recommendations.extend(self._weak_topic_resources())
        
        # 2. Trending recommendations (latest/mostly used resources)
        recommendations.extend(self._trending_resources())

        # Deduplicate by resource ID to avoid showing the same resource twice
        seen_res_ids = set()
        unique_recs = []
        for rec in recommendations:
            res_id = rec.get('metadata', {}).get('resource_id')
            if res_id not in seen_res_ids:
                if res_id:
                    seen_res_ids.add(res_id)
                unique_recs.append(rec)

        # Score and rank (we can still use the internal score to order them)
        scored = [self._score_simple(r) for r in unique_recs]
        
        # Sort by reason: trending first, then weak_topic
        # Let's just rely on final_score or group them in frontend
        scored.sort(key=lambda x: x['final_score'], reverse=True)

        # Save to database
        saved = []
        for rec_data in scored[:limit]:
            rec = Recommendation.objects.create(
                user=self.user,
                recommendation_type=rec_data['type'],
                title=rec_data['title'],
                description=rec_data['description'],
                reason=rec_data['reason'],
                reason_detail=rec_data['reason_detail'],
                relevance_score=rec_data.get('relevance_score', 80),
                priority_score=rec_data.get('priority_score', 80),
                confidence_score=rec_data.get('confidence_score', 80),
                final_score=rec_data.get('final_score', 80),
                topic=rec_data.get('topic', ''),
                subject=rec_data.get('subject', ''),
                difficulty=rec_data.get('difficulty', 'medium'),
                resource_url=rec_data.get('resource_url', ''),
                metadata=rec_data.get('metadata', {}),
            )
            saved.append(rec)

        return saved

    def get_up_next(self, limit=8):
        """Removed up next logic per user request."""
        from recommendations.models import Recommendation
        return Recommendation.objects.none()

    def _weak_topic_resources(self):
        """Find real resources matching the user's weak topics."""
        from recommendations.models import TopicMastery
        from resources.models import Resource
        
        all_weak = TopicMastery.objects.filter(
            user=self.user, is_weak=True
        ).order_by('accuracy_percentage')
        
        subject_counts = {}
        for w in all_weak:
            if w.subject:
                subject_counts[w.subject] = subject_counts.get(w.subject, 0) + 1

        weak = all_weak[:5]

        recs = []
        seen_res_ids = set()
        generalized_subjects = set()

        for mastery in weak:
            topic_query = mastery.topic_name
            subject_query = mastery.subject
            
            q_objects = Q()
            is_general = False
            
            # If the user is weak in many subtopics (>= 3) for this subject, generalize
            if subject_query and subject_counts.get(subject_query, 0) >= 3:
                if subject_query in generalized_subjects:
                    continue  # Already provided general recommendations for this subject
                
                is_general = True
                generalized_subjects.add(subject_query)
                q_objects |= Q(title__icontains=subject_query) | Q(subject__icontains=subject_query) | Q(description__icontains=subject_query)
            else:
                if topic_query:
                    q_objects |= Q(title__icontains=topic_query) | Q(description__icontains=topic_query) | Q(subject__icontains=topic_query)
                if subject_query:
                    q_objects |= Q(title__icontains=subject_query) | Q(subject__icontains=subject_query)
                
            if not q_objects:
                continue

            matching_resources = Resource.objects.filter(q_objects).distinct().order_by('-created_at')[:3]
            
            for res in matching_resources:
                if res.id in seen_res_ids:
                    continue
                seen_res_ids.add(res.id)
                res_url = res.file.url if (hasattr(res, 'file') and res.file) else res.url
                rtype = res.resource_type # video, pdf, or article
                
                if is_general:
                    desc = res.description or f'General practice for {subject_query} to cover multiple weak areas.'
                    r_detail = f'Recommended for comprehensive improvement in {subject_query}'
                    disp_topic = subject_query
                else:
                    desc = res.description or f'Recommended to help you improve in {mastery.topic_name}.'
                    r_detail = f'Recommended based on your weakness in {mastery.topic_name}'
                    disp_topic = mastery.topic_name

                recs.append({
                    'type': rtype,
                    'title': f'{res.title}',
                    'description': desc,
                    'reason': 'weak_topic_resource',
                    'reason_detail': r_detail,
                    'topic': disp_topic,
                    'subject': mastery.subject,
                    'difficulty': 'medium',
                    'resource_url': res_url,
                    'metadata': {'resource_id': res.id, 'accuracy': mastery.accuracy_percentage},
                    '_score': max(0, 100 - mastery.accuracy_percentage) + (5 if is_general else 0),
                })
                
        # FALLBACK: If no exact matches are found, or user has no weak topics yet, 
        # recommend some general resources so the section still appears.
        if not recs:
            fallback_resources = Resource.objects.order_by('?')[:4]
            for res in fallback_resources:
                if res.id in seen_res_ids:
                    continue
                seen_res_ids.add(res.id)
                res_url = res.file.url if (hasattr(res, 'file') and res.file) else res.url
                rtype = res.resource_type
                recs.append({
                    'type': rtype,
                    'title': f'{res.title}',
                    'description': res.description or 'A highly recommended resource for your general preparation.',
                    'reason': 'weak_topic_resource',
                    'reason_detail': 'Recommended for your overall exam preparation',
                    'topic': 'General Practice',
                    'subject': res.subject,
                    'difficulty': 'medium',
                    'resource_url': res_url,
                    'metadata': {'resource_id': res.id},
                    '_score': 75,
                })

        return recs

    def _trending_resources(self):
        """Fetch trending/mostly used resources."""
        from resources.models import Resource

        # Order by view_count (mostly used) then created_at (newest)
        trending_resources = Resource.objects.order_by('-view_count', '-created_at')[:8]
        recs = []
        for res in trending_resources:
            res_url = res.file.url if (hasattr(res, 'file') and res.file) else res.url
            rtype = res.resource_type
            recs.append({
                'type': rtype,
                'title': res.title,
                'description': res.description or 'Popular resource among students right now.',
                'reason': 'trending',
                'reason_detail': 'Trending Today - Mostly used resource',
                'topic': '',
                'subject': '',
                'difficulty': 'medium',
                'resource_url': res_url,
                'metadata': {'resource_id': res.id},
                '_score': 80,
            })
        return recs

    def _score_simple(self, rec):
        """Assign a final score simply for sorting."""
        score = rec.get('_score', 80)
        # Give trending slightly higher base so they can appear top, or random variations
        if rec['reason'] == 'trending':
            score += 15
        elif rec['reason'] == 'weak_topic_resource':
            score += 10
            
        score += random.uniform(-2, 2)
        rec['final_score'] = round(max(0, min(100, score)), 1)
        if '_score' in rec:
            del rec['_score']
        return rec
