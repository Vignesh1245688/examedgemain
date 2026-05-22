from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.views import UserViewSet
from exams.views import ExamViewSet, CategoryViewSet, SubmitExamView, AdminPendingExamsView
from quiz.views import QuizViewSet
from resources.views import VideoResourceAPIView, PDFResourceAPIView, UserResourceAPIView
from news.views import NewsAPIView

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'exams', ExamViewSet, basename='exam')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'quiz', QuizViewSet, basename='quiz')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/exams/submit/', SubmitExamView.as_view(), name='exam-submit'),
    path('api/exams/pending/', AdminPendingExamsView.as_view(), name='exam-pending'),
    path('api/', include(router.urls)),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/news/', NewsAPIView.as_view(), name='news'),
    path('api/resources/videos/', VideoResourceAPIView.as_view(), name='resources-videos'),
    path('api/resources/pdfs/', PDFResourceAPIView.as_view(), name='resources-pdfs'),
    path('api/resources/community/', UserResourceAPIView.as_view(), name='resources-community'),
    path('api/practice-quiz/', include('practice_quiz.urls')),
    path('api/groups/', include('groups.urls')),
    path('api/recommendations/', include('recommendations.urls')),
    path('api/admin-panel/', include('admin_panel.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
