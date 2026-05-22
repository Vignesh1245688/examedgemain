import os
import tempfile
import pdfplumber
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from .models import PracticeQuizResult, QuizTemplate, FlashcardSet
from .serializers import PracticeQuizResultSerializer, QuizTemplateSerializer, FlashcardSetSerializer
from django.db.models import Sum, Count, F, Avg
from django.db.models.functions import TruncDate

def call_ai(prompt, system_prompt="You are an AI assistant. Return JSON only."):
    groq_api_key = os.getenv("GROQ_API_KEY")
    if groq_api_key:
        try:
            from groq import Groq
            client = Groq(api_key=groq_api_key)
            completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.7,
                max_tokens=4096,
                response_format={"type": "json_object"}
            )
            raw = completion.choices[0].message.content
            return json.loads(raw.strip())
        except Exception as e:
            print(f"Groq error: {e}")

    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if gemini_api_key:
        try:
            from google import genai
            client = genai.Client(api_key=gemini_api_key)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"{system_prompt}\n\n{prompt}",
            )
            raw = response.text
            if "```json" in raw:
                raw = raw.split("```json")[1].split("```")[0]
            elif "```" in raw:
                raw = raw.split("```")[1].split("```")[0]
            return json.loads(raw.strip())
        except Exception as e:
            print(f"Gemini error: {e}")

    return None

class AnalyzeDocumentView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        file_obj = request.data.get('file')
        if not file_obj:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                for chunk in file_obj.chunks():
                    tmp.write(chunk)
                tmp_path = tmp.name

            text = ""
            with pdfplumber.open(tmp_path) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
            os.remove(tmp_path)

            text = text[:20000] # Limit for API
            if not text.strip():
                return Response({'error': 'Could not extract text'}, status=status.HTTP_400_BAD_REQUEST)

            prompt = f"""Analyze the text and return a JSON object with:
- "topics": array of strings (top 5-10 main concepts/topics)
- "keywords": array of strings
Text: {text}"""
            
            result = call_ai(prompt, "You are an AI document analyzer. Always return JSON with 'topics' and 'keywords' arrays.")
            if result:
                return Response({'topics': result.get('topics', []), 'keywords': result.get('keywords', []), 'text': text}, status=status.HTTP_200_OK)
            
            return Response({'topics': ['General', 'Concepts'], 'keywords': [], 'text': text}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GenerateQuizView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        text = request.data.get('text', '')
        difficulty = request.data.get('difficulty', 'Medium')
        num_questions = int(request.data.get('num_questions', 5))
        question_types = request.data.get('question_types', ['mcq']) # array of types
        selected_topics = request.data.get('topics', [])
        mode = request.data.get('mode', 'Standard')

        if not text:
            return Response({'error': 'Text content missing'}, status=status.HTTP_400_BAD_REQUEST)

        topics_str = ", ".join(selected_topics) if selected_topics else "the entire text"
        types_str = ", ".join(question_types)

        prompt = f"""Generate a quiz with {num_questions} questions based on this text.
Difficulty: {difficulty}
Question Types to include: {types_str} (distribute evenly)
Focus topics (if any): {topics_str}
Generation Mode: {mode}

Return output as a JSON object with a 'questions' array. Each question must have:
- 'type': string ('mcq', 'true_false', 'fill_blanks', 'short_answer')
- 'question': string
- 'options': array of strings (only for mcq)
- 'correctAnswer': integer index for mcq, or string for true_false/fill_blanks/short_answer
- 'explanation': detailed educational explanation
- 'reference': quote from the text supporting the answer
- 'topic': the topic this question relates to

Text: {text[:15000]}"""

        result = call_ai(prompt, "You are a professional EdTech quiz generator. Return valid JSON only.")
        if result and 'questions' in result:
            questions = result['questions']
            # Dynamic timer calculation
            base_time = 0
            for q in questions:
                if q.get('type') == 'mcq': base_time += 60
                elif q.get('type') == 'true_false': base_time += 30
                elif q.get('type') == 'short_answer': base_time += 120
                else: base_time += 45
            
            if difficulty == 'Hard': base_time = int(base_time * 1.5)
            elif difficulty == 'Easy': base_time = int(base_time * 0.8)

            return Response({'questions': questions, 'recommended_timer': base_time}, status=status.HTTP_200_OK)

        # Fallback dummy questions
        return Response({
            'questions': [
                {"type": "mcq", "question": "Placeholder", "options": ["A", "B", "C", "D"], "correctAnswer": 0, "explanation": "Failed to generate.", "reference": "", "topic": "General"}
            ],
            'recommended_timer': 300
        }, status=status.HTTP_200_OK)

class SaveQuizResultView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = PracticeQuizResultSerializer(data=request.data)
        if serializer.is_valid():
            result = serializer.save(user=request.user)

            # ── Save wrongly-answered questions for Daily Revision ──
            try:
                from recommendations.models import DailyRevisionQuestion
                from django.utils import timezone as tz

                wrong_questions = request.data.get('wrong_questions', [])
                for wq in wrong_questions:
                    DailyRevisionQuestion.objects.create(
                        user=request.user,
                        date=tz.now().date(),
                        question_text=wq.get('question', ''),
                        question_type=wq.get('type', 'mcq'),
                        options=wq.get('options', []),
                        correct_answer=str(wq.get('correctAnswer', '')),
                        user_answer=str(wq.get('userAnswer', '')),
                        explanation=wq.get('explanation', ''),
                        reference=wq.get('reference', ''),
                        topic=wq.get('topic', ''),
                        difficulty=wq.get('difficulty', 'medium'),
                        source_quiz_id=result.id,
                        source_quiz_title=result.title,
                    )
            except Exception as e:
                print(f"Daily revision save error (non-blocking): {e}")

            # ── AI Engine Integration ──
            try:
                from recommendations.services import WeakTopicDetector, AdaptiveEngine, SpacedRepetitionEngine
                from recommendations.models import UserActivity, LearningStreak

                detector = WeakTopicDetector(request.user)

                # Update topic mastery from topics_accuracy
                if result.topics_accuracy:
                    for topic, accuracy in result.topics_accuracy.items():
                        total_est = max(1, result.total_questions // max(len(result.topics_accuracy), 1))
                        correct_est = int(total_est * accuracy / 100)
                        detector.update_topic_from_quiz(
                            topic_name=topic,
                            correct=correct_est,
                            total=total_est,
                            time_seconds=result.time_taken_seconds // max(len(result.topics_accuracy), 1),
                        )

                # Log activity
                UserActivity.objects.create(
                    user=request.user,
                    activity_type='quiz_attempt',
                    topic=result.title,
                    score=result.score,
                    max_score=result.total_questions,
                    time_spent_seconds=result.time_taken_seconds,
                    completed=True,
                    metadata={'quiz_id': result.id, 'file': result.file_name},
                )

                # Update streak
                streak, _ = LearningStreak.objects.get_or_create(user=request.user)
                streak.record_activity(xp_earned=15)

                # Run adaptive engine
                adaptive = AdaptiveEngine(request.user)
                adaptive.evaluate_and_adapt()

                # Schedule spaced repetition for weak topics
                sr = SpacedRepetitionEngine(request.user)
                if result.weak_topics:
                    for topic in result.weak_topics:
                        if isinstance(topic, str):
                            sr.process_review(topic, quality_rating=2)

            except Exception as e:
                print(f"AI Engine update error (non-blocking): {e}")

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class QuizHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        results = PracticeQuizResult.objects.filter(user=request.user).order_by('-created_at')
        serializer = PracticeQuizResultSerializer(results, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None, *args, **kwargs):
        try:
            result = PracticeQuizResult.objects.get(pk=pk, user=request.user)
            result.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except PracticeQuizResult.DoesNotExist:
            return Response({"error": "Not found."}, status=status.HTTP_404_NOT_FOUND)

class QuizTemplateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        templates = QuizTemplate.objects.filter(user=request.user)
        return Response(QuizTemplateSerializer(templates, many=True).data)

    def post(self, request):
        serializer = QuizTemplateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        try:
            template = QuizTemplate.objects.get(pk=pk, user=request.user)
            template.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except QuizTemplate.DoesNotExist:
            return Response({"error": "Not found."}, status=status.HTTP_404_NOT_FOUND)

class FlashcardSetView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        text = request.data.get('text')
        if not text:
            return Response({'error': 'No text provided'}, status=status.HTTP_400_BAD_REQUEST)

        prompt = f"Generate 10 concise flashcards from this text. Return JSON object with 'flashcards' array (each with 'front' and 'back'). Text: {text[:10000]}"
        result = call_ai(prompt, "You are a flashcard generator. Return valid JSON only.")
        
        flashcards = result.get('flashcards', []) if result else []
        
        s = FlashcardSet.objects.create(user=request.user, title=request.data.get('title', 'Quick Revision'), flashcards=flashcards)
        return Response(FlashcardSetSerializer(s).data, status=status.HTTP_201_CREATED)
        
    def get(self, request):
        sets = FlashcardSet.objects.filter(user=request.user).order_by('-created_at')
        return Response(FlashcardSetSerializer(sets, many=True).data)

class AnalyticsDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        results = PracticeQuizResult.objects.filter(user=user)
        
        total_quizzes = results.count()
        if total_quizzes == 0:
            return Response({
                "total_quizzes": 0,
                "overall_accuracy": 0,
                "topic_performance": {},
                "weak_topics": [],
                "strong_topics": [],
                "history_trends": []
            }, status=status.HTTP_200_OK)
            
        total_score = results.aggregate(Sum('score'))['score__sum'] or 0
        total_qs = results.aggregate(Sum('total_questions'))['total_questions__sum'] or 1
        accuracy = (total_score / total_qs) * 100

        # Topic aggregation
        topic_stats = {}
        for r in results:
            if r.topics_accuracy:
                for t, acc in r.topics_accuracy.items():
                    if t not in topic_stats: topic_stats[t] = []
                    topic_stats[t].append(acc)
                    
        topic_avg = {k: sum(v)/len(v) for k, v in topic_stats.items()}
        weak_topics = [k for k, v in topic_avg.items() if v < 50]
        strong_topics = [k for k, v in topic_avg.items() if v >= 75]

        history_trends = list(results.order_by('created_at').values('created_at', 'score', 'total_questions'))

        return Response({
            "total_quizzes": total_quizzes,
            "overall_accuracy": round(accuracy, 2),
            "topic_performance": topic_avg,
            "weak_topics": weak_topics,
            "strong_topics": strong_topics,
            "history_trends": history_trends
        })
