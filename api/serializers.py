from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Blog, Contact, Project

class BlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = [
            "id",
            "title",
            "content",
            "image",
            "created",
            "updated",
        ]

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            "id",
            "title",
            "description",
            "technologies",
            "github",
            "live_demo",
            "image",
            "created",
        ]

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = [
            "id",
            "name",
            "email",
            "message",
            "created",
            "is_read",
        ]

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']
        extra_kwargs = {
            "password": {
                "write_only": True,
                "min_length": 8
                }
        }

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
