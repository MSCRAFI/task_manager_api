from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Task
        fields = (
            'id', 'users', 'description',
            'priority', 'status', 'due_date',
            'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'user', 'created_at', 'updated_at'
        )

    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError("Title cannot be blank.")
        return value.strip()

class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'priority',
            'status', 'due_date'
        ]

    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError("Title cannot be blank.")
        return value.strip()

    def create(self, validated_data):
        # auto assign the logged in user
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
