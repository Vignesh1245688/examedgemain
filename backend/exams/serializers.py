from rest_framework import serializers
from django.utils import timezone
from .models import Category, Exam, ExamDate

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ExamDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamDate
        fields = ('id', 'date_type', 'date')

class ExamSerializer(serializers.ModelSerializer):
    dates = ExamDateSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    is_open = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Exam
        fields = '__all__'

    def get_is_open(self, obj):
        if not obj.application_start_date or not obj.application_end_date:
            return False
        now = timezone.now().date()
        return obj.application_start_date <= now <= obj.application_end_date

    def get_status(self, obj):
        if not obj.application_start_date or not obj.application_end_date:
            return "Closed"
        now = timezone.now().date()
        if now < obj.application_start_date:
            return "Upcoming"
        if now > obj.application_end_date:
            return "Closed"
        return "Open"
