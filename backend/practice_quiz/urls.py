from django.urls import path
from .views import (
    AnalyzeDocumentView, GenerateQuizView, SaveQuizResultView, 
    QuizHistoryView, QuizTemplateView, FlashcardSetView, AnalyticsDashboardView
)

urlpatterns = [
    path('analyze/', AnalyzeDocumentView.as_view(), name='analyze-document'),
    path('generate/', GenerateQuizView.as_view(), name='generate-quiz'),
    path('save-result/', SaveQuizResultView.as_view(), name='save-quiz-result'),
    path('history/', QuizHistoryView.as_view(), name='quiz-history'),
    path('history/<int:pk>/', QuizHistoryView.as_view(), name='quiz-history-detail'),
    path('templates/', QuizTemplateView.as_view(), name='quiz-templates'),
    path('templates/<int:pk>/', QuizTemplateView.as_view(), name='quiz-templates-detail'),
    path('flashcards/', FlashcardSetView.as_view(), name='flashcards'),
    path('analytics/', AnalyticsDashboardView.as_view(), name='analytics-dashboard'),
]
