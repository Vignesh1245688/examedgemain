from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import User, Profile, Notification
from .serializers import UserSerializer, NotificationSerializer
from exams.models import Exam

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'register']:
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"user": UserSerializer(user).data, "message": "User created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def profile(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='bookmark/(?P<exam_id>[^/.]+)')
    def bookmark(self, request, exam_id=None):
        try:
            exam = Exam.objects.get(id=exam_id)
            profile = request.user.profile
            if exam in profile.bookmarks.all():
                profile.bookmarks.remove(exam)
                return Response({"message": "Bookmark removed"}, status=status.HTTP_200_OK)
            else:
                profile.bookmarks.add(exam)
                return Response({"message": "Bookmark added"}, status=status.HTTP_200_OK)
        except Exam.DoesNotExist:
            return Response({"error": "Exam not found"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def notifications(self, request):
        queryset = Notification.objects.filter(user=request.user).order_by('-created_at')
        serializer = NotificationSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='notifications/(?P<notification_id>[^/.]+)/read')
    def mark_notification_read(self, request, notification_id=None):
        try:
            notification = Notification.objects.get(id=notification_id, user=request.user)
            notification.is_read = True
            notification.save()
            return Response({"status": "Notification marked as read"}, status=status.HTTP_200_OK)
        except Notification.DoesNotExist:
            return Response({"error": "Notification not found"}, status=status.HTTP_404_NOT_FOUND)
