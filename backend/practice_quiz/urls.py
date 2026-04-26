from django.urls import path
from .views import GenerateQuizView, SaveQuizResultView, QuizHistoryView

urlpatterns = [
    path('generate/', GenerateQuizView.as_view(), name='generate-quiz'),
    path('save-result/', SaveQuizResultView.as_view(), name='save-quiz-result'),
    path('history/', QuizHistoryView.as_view(), name='quiz-history'),
]
