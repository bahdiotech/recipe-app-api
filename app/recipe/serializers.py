"""Serializer for recipe APIs"""
from rest_framework import serializers

from core.models import Recipe


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipe APIs"""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'title',
            'link',
            'price',
            'time_minutes',
        )
        read_only_fields = ('id',)


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view APIs"""

    class Meta(RecipeSerializer.Meta):
        model = Recipe
        fields = RecipeSerializer.Meta.fields + ('description',)
