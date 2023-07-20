from rest_framework import serializers
from django.utils.crypto import get_random_string

from authentication.models import User


class UserSerializer(serializers.ModelSerializer):

    token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'email_verified',
                  'verify_token', 'password', 'token', 'created_at')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = super(UserSerializer, self).create(validated_data)
        user.verify_token = get_random_string(length=32)
        user.save()
        return user
