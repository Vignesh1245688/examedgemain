from rest_framework import serializers
from .models import Group, GroupMember, Message, Material
from users.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']

class GroupMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = GroupMember
        fields = ['id', 'group', 'user', 'role', 'is_approved', 'joined_at']

class GroupSerializer(serializers.ModelSerializer):
    # Depending on context, we might want to return members
    members = GroupMemberSerializer(many=True, read_only=True)
    
    class Meta:
        model = Group
        fields = ['id', 'name', 'description', 'exam_type', 'exam_name', 'created_at', 'members']

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    class Meta:
        model = Message
        fields = ['id', 'group', 'sender', 'content', 'file', 'timestamp']

class MaterialSerializer(serializers.ModelSerializer):
    uploaded_by = UserSerializer(read_only=True)
    class Meta:
        model = Material
        fields = ['id', 'group', 'uploaded_by', 'title', 'file', 'link', 'timestamp']
