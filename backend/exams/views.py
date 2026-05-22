from rest_framework import viewsets, filters, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from .models import Exam, Category
from .serializers import ExamSerializer, CategorySerializer

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ExamViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Exam.objects.filter(is_approved=True).prefetch_related('dates', 'category')
    serializer_class = ExamSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = {
        'category__slug': ['exact'],
        'category__name': ['icontains'],
    }
    search_fields = ['name', 'conducting_body', 'category__name']

class SubmitExamView(APIView):
    """View for regular users to submit a new exam for admin approval."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        category_id = request.data.get('category')
        name = request.data.get('name')
        conducting_body = request.data.get('conducting_body')
        eligibility = request.data.get('eligibility')
        syllabus = request.data.get('syllabus')

        if not all([category_id, name, conducting_body, eligibility, syllabus]):
            return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response({'error': 'Invalid category'}, status=status.HTTP_400_BAD_REQUEST)

        exam = Exam.objects.create(
            name=name,
            category=category,
            conducting_body=conducting_body,
            eligibility=eligibility,
            syllabus=syllabus,
            official_link=request.data.get('official_link', ''),
            apply_link=request.data.get('apply_link', ''),
            uploaded_by=request.user,
            is_approved=False # Requires admin approval
        )
        
        # We can add dates too if needed
        return Response({'status': 'Exam submitted successfully and is pending approval.', 'id': exam.id}, status=status.HTTP_201_CREATED)

class AdminPendingExamsView(APIView):
    """View for admins to see pending exams and approve them."""
    permission_classes = [IsAdminUser]

    def get(self, request):
        pending_exams = Exam.objects.filter(is_approved=False).order_by('-created_at')
        serializer = ExamSerializer(pending_exams, many=True)
        return Response(serializer.data)

    def post(self, request):
        action = request.data.get('action') # 'approve' or 'reject'
        exam_id = request.data.get('exam_id')

        try:
            exam = Exam.objects.get(id=exam_id, is_approved=False)
        except Exam.DoesNotExist:
            return Response({'error': 'Pending exam not found'}, status=status.HTTP_404_NOT_FOUND)

        if action == 'approve':
            exam.is_approved = True
            exam.save()
            return Response({'status': 'Exam approved and published'})
        elif action == 'reject':
            exam.delete()
            return Response({'status': 'Exam rejected and deleted'})
        
        return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)
