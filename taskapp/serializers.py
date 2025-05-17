from rest_framework import serializers
from .models import TaskMakerUser, Project, Task, Comment, File, ProjectMember, Reminder
from django.utils import timezone

class TaskSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'name', 'date', 'status', 'project']

class TaskMakerUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskMakerUser
        fields = '__all__'

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'

class TaskSerializer(serializers.ModelSerializer):
    task_make_date = serializers.DateTimeField(read_only=True)  # Ожидаем дату с временной зоной

    class Meta:
        model = Task
        fields = '__all__'  # Включаем все поля модели

    def create(self, validated_data):
        validated_data['task_make_date'] = timezone.now()  # Создаем aware дату
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data['task_make_date'] = timezone.now()  # Обновляем aware дату
        return super().update(instance, validated_data)

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = '__all__'

class ProjectMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectMember
        fields = '__all__'

class ReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminder
        fields = '__all__'
