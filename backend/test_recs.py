import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from recommendations.services import RecommendationEngine
from recommendations.models import Recommendation

User = get_user_model()
user = User.objects.first()

if user:
    print(f"Testing recommendations for user: {user.username}")
    engine = RecommendationEngine(user)
    
    print("--- Testing get_up_next() ---")
    try:
        up_next = engine.get_up_next()
        print(f"Success! Found {len(up_next)} up next items.")
    except Exception as e:
        print(f"ERROR in get_up_next: {e}")
        
    print("--- Testing generate_feed() ---")
    try:
        engine.generate_feed(limit=5)
        recs = Recommendation.objects.filter(user=user)
        print(f"Success! User now has {recs.count()} recommendations in DB.")
        for r in recs:
            print(f"- {r.title} (Reason: {r.reason}, Score: {r.final_score:.2f})")
    except Exception as e:
        print(f"ERROR in generate_feed: {e}")
else:
    print("No users found to test with.")
