from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from .models import Group, GroupMember, Message, Material
from .serializers import GroupSerializer, GroupMemberSerializer, MessageSerializer, MaterialSerializer
from users.models import Notification

DELETE_WINDOW_SECONDS = 120  # 2 minutes

class IsGroupMemberOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # obj could be a Group, Message, or Material
        group = getattr(obj, 'group', obj) if not isinstance(obj, Group) else obj
        
        # Check if user is an approved member
        is_member = GroupMember.objects.filter(group=group, user=request.user, is_approved=True).exists()
        return is_member

class GroupViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GroupSerializer

    def get_queryset(self):
        # Allow searching/filtering
        queryset = Group.objects.all()
        exam_type = self.request.query_params.get('exam_type')
        exam_name = self.request.query_params.get('exam_name')
        if exam_type:
            queryset = queryset.filter(exam_type=exam_type)
        if exam_name:
            queryset = queryset.filter(exam_name__icontains=exam_name)
        return queryset

    def perform_create(self, serializer):
        # Create group and assign creator as Admin
        group = serializer.save()
        GroupMember.objects.create(group=group, user=self.request.user, role='Admin', is_approved=True)

    def destroy(self, request, *args, **kwargs):
        group = self.get_object()
        # Check if the user is an admin of the group
        if not GroupMember.objects.filter(group=group, user=request.user, role='Admin', is_approved=True).exists():
            return Response({'error': 'Only admins can delete this group.'}, status=status.HTTP_403_FORBIDDEN)
        group.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def request_join(self, request, pk=None):
        group = self.get_object()
        user = request.user
        member, created = GroupMember.objects.get_or_create(group=group, user=user)
        if created:
            return Response({'status': 'Join request sent.'}, status=status.HTTP_201_CREATED)
        return Response({'status': 'Request already exists.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def approve_member(self, request, pk=None):
        group = self.get_object()
        # Ensure request.user is Admin of this group
        if not GroupMember.objects.filter(group=group, user=request.user, role='Admin', is_approved=True).exists():
            return Response({'error': 'Only admins can approve members.'}, status=status.HTTP_403_FORBIDDEN)
        
        user_id = request.data.get('user_id')
        try:
            member = GroupMember.objects.get(group=group, user_id=user_id)
            member.is_approved = True
            member.save()

            # Create notification for the approved user
            Notification.objects.create(
                user=member.user,
                message=f"Your request to join the group '{group.name}' has been approved.",
                group_id=group.id
            )

            return Response({'status': 'Member approved.'}, status=status.HTTP_200_OK)
        except GroupMember.DoesNotExist:
            return Response({'error': 'Member request not found.'}, status=status.HTTP_404_NOT_FOUND)

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.action == 'list':
            group_id = self.request.query_params.get('group_id')
            if group_id:
                return Message.objects.filter(group_id=group_id).order_by('timestamp')
            return Message.objects.none()
        return Message.objects.all()

    def perform_create(self, serializer):
        # Assuming group is passed in data
        group_id = self.request.data.get('group')
        group = get_object_or_404(Group, pk=group_id)
        
        # Check permission manually
        if not GroupMember.objects.filter(group=group, user=self.request.user, is_approved=True).exists():
            raise serializers.ValidationError("Not an approved member of this group.")
            
        serializer.save(sender=self.request.user)
        
        # Notify other approved group members
        other_members = GroupMember.objects.filter(group=group, is_approved=True).exclude(user=self.request.user)
        notifications = []
        for member in other_members:
            notifications.append(
                Notification(
                    user=member.user,
                    message=f"New message from {self.request.user.username} in group '{group.name}'",
                    group_id=group.id
                )
            )
        if notifications:
            Notification.objects.bulk_create(notifications)

    def destroy(self, request, *args, **kwargs):
        message = self.get_object()
        if message.sender != request.user:
            return Response({'error': 'You can only delete your own messages.'}, status=status.HTTP_403_FORBIDDEN)
        elapsed = timezone.now() - message.timestamp
        if elapsed > timedelta(seconds=DELETE_WINDOW_SECONDS):
            return Response({'error': 'You can only delete messages within 2 minutes of sending.'}, status=status.HTTP_403_FORBIDDEN)
        message.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class MaterialViewSet(viewsets.ModelViewSet):
    serializer_class = MaterialSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.action == 'list':
            group_id = self.request.query_params.get('group_id')
            if group_id:
                return Material.objects.filter(group_id=group_id).order_by('-timestamp')
            return Material.objects.none()
        return Material.objects.all()

    def perform_create(self, serializer):
        group_id = self.request.data.get('group')
        group = get_object_or_404(Group, pk=group_id)
        
        if not GroupMember.objects.filter(group=group, user=self.request.user, is_approved=True).exists():
            raise serializers.ValidationError("Not an approved member of this group.")
            
        serializer.save(uploaded_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        material = self.get_object()
        if material.uploaded_by != request.user:
            return Response({'error': 'You can only delete materials you uploaded.'}, status=status.HTTP_403_FORBIDDEN)
        elapsed = timezone.now() - material.timestamp
        if elapsed > timedelta(seconds=DELETE_WINDOW_SECONDS):
            return Response({'error': 'You can only delete materials within 2 minutes of uploading.'}, status=status.HTTP_403_FORBIDDEN)
        material.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
