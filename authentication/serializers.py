
from rest_framework import serializers
from .models import User
from django.contrib import auth
from rest_framework.exceptions import AuthenticationFailed


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=68, min_length=6, write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def validate(self, attrs):
        username = attrs.get("username", "")
        email = attrs.get("email", "")

        if not username.isalnum():
            raise serializers.ValidationError(
                "The username should only contain alphanumeric character")
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=555)

    class Meta:
        model = User
        fields = ["token"]


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=3)
    password = serializers.CharField(
        max_length=68, min_length=6, write_only=True)
    username = serializers.CharField(
        max_length=255, min_length=3, read_only=True)
    tokens = serializers.CharField(
        max_length=68, min_length=6, read_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "username", "tokens"]

    def validate(self, attrs):
        email = attrs.get("email", "")
        password = attrs.get("password", "")

        user = auth.authenticate(email=email, password=password)

        if not user:
            raise AuthenticationFailed("Invalid Credentails! Try again")

        if not user.is_verified:  # type: ignore
            raise AuthenticationFailed("Email is not verified! Try again", 400)

        if not user.is_active:
            raise AuthenticationFailed("Account disabled contact admin")

        return {
            "email": user.email,  # type: ignore
            "username": user.username,  # type: ignore
            "tokens": user.tokens()  # type: ignore
        }
