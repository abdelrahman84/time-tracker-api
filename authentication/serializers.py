from rest_framework import serializers
from django.utils.crypto import get_random_string
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import json as simplejson
from django.core import validators
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.models import User


class UserSerializer(serializers.ModelSerializer):

    token = serializers.CharField(max_length=255, read_only=True)

    password = serializers.CharField(max_length=128, required=True, validators=[
        validators.RegexValidator(
            regex=r'^(?=.*[\d])(?=.*[A-Z])(?=.*[a-z])(?=.*[@#$])[\w\d@#$]{8,}$',
            message='Please enter a strong password'
        )
    ])

    access_tokens = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'email_verified',
                  'verify_token', 'password', 'token', 'created_at', 'access_tokens')
        extra_kwargs = {'password': {'write_only': True}}

    def get_access_tokens(self, user):
        tokens = RefreshToken.for_user(user)
        refresh = str(tokens)
        access = str(tokens.access_token)

        data = {
            "refresh": refresh,
            "access": access
        }

        return data

    def to_representation(self, instance):
        representation = super(
            UserSerializer, self).to_representation(instance)
        representation['password'] = ''
        representation['verify_token'] = ''
        return representation

    def create(self, validated_data):
        user = super(UserSerializer, self).create(validated_data)
        user.verify_token = get_random_string(length=32)
        user.password = make_password(validated_data["password"])
        user.save()
        return user


class VerifyTokenSerializer(serializers.Serializer):

    verify_token = serializers.CharField(required=True)


class CheckEmailSerializer(serializers.Serializer):

    email = serializers.CharField(required=True)


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = self.get_token(self.user)

        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        user = UserSerializer(self.user)

        data['user'] = simplejson.dumps(user.data)
        return data


class VerifyLoginSerializer(serializers.Serializer):

    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)


class ResetPasswordSerializer(serializers.Serializer):
    reset_token = serializers.CharField(required=True)
    password = serializers.CharField(required=True, validators=[
        validators.RegexValidator(
            # Password must contain at least 8 characters, one uppercase, one lowercase, one number and one special character
            regex=r'^(?=.*\d)(?=.*[A-Z])(?=.*[a-z])(?=.*[^A-Za-z0-9])(.{8,})$',
            message='Please enter a strong password'
        )
    ])
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data
