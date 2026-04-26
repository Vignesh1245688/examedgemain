from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Exam, Category
from .serializers import ExamSerializer, CategorySerializer

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ExamViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Exam.objects.all().prefetch_related('dates', 'category')
    serializer_class = ExamSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = {
        'category__slug': ['exact'],
        'category__name': ['icontains'],
    }
    search_fields = ['name', 'conducting_body', 'category__name']
