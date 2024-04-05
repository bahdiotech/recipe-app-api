"""Serializers for the user api views"""
from django.contrib.auth import (
                                 get_user_model,
                                 authenticate,
                                 )
from django.utils.translation import gettext as _

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user Object Model"""

    class Meta:
        model = get_user_model()
        fields = ('email', 'name', 'password')
        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 5,
                'style': {'input_type': 'password'}
            }
        }

    def create(self, validated_data):
        """Create and return user encrypted password"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update and return user encrypted password"""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user Auth token"""
    email = serializers.EmailField(max_length=30)
    password = serializers.CharField(
        max_length=30,
        style={'input_type': 'password'},
        trim_whitespace=False,
        )

    def validate(self, attrs):
        """Validate and authenticate the user"""
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
            )
        if not user:
            msg = _('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg, code='authorization')
        attrs['user'] = user
        return attrs
