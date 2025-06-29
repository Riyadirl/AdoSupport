from rest_framework import serializers
from .models import User, UserProfile
from django.contrib.auth import authenticate

# ------------------------------------ User and User Profile ------------------------------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = "__all__"
        read_only_fields = ["id", "user", "created_at"]

        def update(self, instance, validated_data):
            validated_data.pop('email', None)
            validated_data.pop('gender', None)
            return super().update(instance, validated_data)

