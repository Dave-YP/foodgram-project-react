from typing import Dict
from django.contrib.auth import get_user_model

from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from users.models import Subscription
from .recipe_serializers import RecipeShortSerializer
from .user_serializers import UserProfileSerializer
User = get_user_model()


class SubscriptionSerializer(UserProfileSerializer):
    """
    Сериализатор для подписки на автора.

    Атрибуты:
        email: адрес электронной почты пользователя.
        username: имя пользователя.
        first_name: имя пользователя.
        last_name: фамилия пользователя.
        is_subscribed: подписка.
        recipes: список короткой информации о рецептах автора.
        recipes_count: количество рецептов автора.

    Методы:
        validate: метод для валидации данных при создании подписки.
        get_recipes: метод для получения списка короткой информации о рецептах.
        get_recipes_count: метод для получения количества рецептов автора.

    """

    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes',
                  'recipes_count')
        read_only_fields = ('email', 'username')

    def validate(self, data: Dict) -> Dict:
        author = self.instance
        user = self.context.get('request').user
        subscription_exists = Subscription.objects.filter(
            author=author, user=user
        ).exists()

        if subscription_exists:
            raise serializers.ValidationError(
                {'subscription': ['Подписка уже есть']}
            )
        if user == author:
            raise serializers.ValidationError(
                {'subscription': ['Нельзя подписаться на себя']}
            )
        return data

    def get_recipes(self, obj):
        recipes = obj.recipes.all()
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeShortSerializer(recipes, many=True, read_only=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.recipes.count()
