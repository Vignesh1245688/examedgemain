from rest_framework import serializers
from .models import User, Profile, Notification
from exams.models import Exam

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('id', 'message', 'is_read', 'group_id', 'created_at')

class ProfileSerializer(serializers.ModelSerializer):
    bookmarks = serializers.PrimaryKeyRelatedField(many=True, queryset=Exam.objects.all(), required=False)

    class Meta:
        model = Profile
        fields = ('state', 'target_exam', 'education_level', 'bookmarks')

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(required=False)
    password = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'password', 'profile')

    def create(self, validated_data):
        profile_data = validated_data.pop('profile', {})
        password = validated_data.pop('password')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            password=password
        )
        Profile.objects.create(user=user, **profile_data)
        return user
