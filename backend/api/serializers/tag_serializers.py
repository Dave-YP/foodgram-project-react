from rest_framework import serializers

from recipes.models import Tag


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Tag.

    Атрибуты:
        id: ID тега.
        name: название тега.
        color: цвет тега.
        slug: уникальный идентификатор тега.

    """

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)
        read_only_fields = fields
