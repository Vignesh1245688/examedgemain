from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .models import Question
from .serializers import QuestionSerializer

class QuizViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        exam_id = self.request.query_params.get('exam')
        if exam_id:
            queryset = queryset.filter(exam_id=exam_id)
        # Add random ordering to fetch, e.g., 10 questions
        return queryset.order_interleaved()[:20] if hasattr(queryset, 'order_interleaved') else queryset.order_by('?')[:20]

    @action(detail=False, methods=['post'])
    def submit(self, request):
        answers = request.data.get('answers', {}) # Dict of {question_id: 'A'}
        if not answers:
            return Response({"error": "No answers provided."}, status=status.HTTP_400_BAD_REQUEST)
        
        score = 0
        total = len(answers)
        results = []
        
        for q_id, user_ans in answers.items():
            try:
                question = Question.objects.get(id=q_id)
                is_correct = (question.correct_answer == user_ans.upper())
                if is_correct:
                    score += 1
                
                results.append({
                    "question_id": q_id,
                    "is_correct": is_correct,
                    "correct_answer": question.correct_answer
                })
            except Question.DoesNotExist:
                continue

        return Response({
            "score": score,
            "total": total,
            "percentage": (score / total * 100) if total > 0 else 0,
            "results": results
        })
