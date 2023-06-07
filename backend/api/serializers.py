from typing import Dict, List
from django.contrib.auth import get_user_model
from django.db.models import F, QuerySet
from django.shortcuts import get_object_or_404

from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.fields import IntegerField, SerializerMethodField
from rest_framework.relations import PrimaryKeyRelatedField

from recipes.models import Ingredient, IngredientInRecipe, Recipe, Tag
from users.models import Subscription

User = get_user_model()


class UserProfileSerializer(UserSerializer):
    """
    Сериализатор профиля пользователя.

    Атрибуты:
        is_subscribed (SerializerMethodField): поле, указывающее,
        подписан ли текущий пользователь на автора.

    Методы:
        get_is_subscribed(obj: User) -> bool: возвращает True, если текущий
        пользователь подписан на автора, иначе False.

    """

    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj: User) -> bool:
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.subscriber.filter(author=obj).exists()


class UserProfileCreateSerializer(UserCreateSerializer):
    """
    Сериализатор для создания пользователя.

    """

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')


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


class RecipeReadSerializer(serializers.ModelSerializer):
    """
    Сериализатор для просмотра информации о рецепте.

    Атрибуты::
        id: уникальный идентификатор рецепт.
        name: название рецепта.
        image: изображение рецепта.
        text: описание рецепта.
        cooking_time: время приготовления рецепта.
        ingredients: список ингредиентов.
        tags: список тегов, связанных с рецептом.
        author: информация об авторе рецепта.
        is_favorited: флаг, указывающий, добавлен ли рецепт в избранное.
        is_in_shopping_cart: флаг, указывающий, добавлен ли рецепт в список.

    """

    tags = TagSerializer(many=True, read_only=True)
    author = UserProfileSerializer(read_only=True)
    ingredients = SerializerMethodField()
    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time',)

    def get_ingredients(self, recipe: Recipe) -> QuerySet[dict]:
        ingredients = recipe.ingredients.values(
            'id', 'name', 'measurement_unit',
            amount=F('ingredientinrecipe__amount')
        )
        return ingredients

    def get_is_favorited(self, recipe: Recipe) -> bool:
        user = self.context.get('request').user

        if user.is_anonymous:
            return False

        return user.favorites.filter(recipe=recipe).exists()

    def get_is_in_shopping_cart(self, recipe: Recipe) -> bool:
        user = self.context.get('request').user

        if user.is_anonymous:
            return False

        return user.shopping_cart.filter(recipe=recipe).exists()


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для добавления ингредиента в рецепт.

    Атрибуты::
        id (IntegerField): ID ингредиента (write_only).
        amount (IntegerField): количество ингредиента в рецепте.

    """

    id = IntegerField(write_only=True)

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')


class RecipeWriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор рецепта.

    Атрибуты:
        id: уникальный идентификатор рецепта.
        author: автор рецепта.
        ingredients: список ингредиентов.
        tags: список тегов.
        image: изображение рецепта.
        name: название рецепта.
        text: описание рецепта.
        cooking_time: время приготовления рецепта в минутах.

    """

    tags = PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True)

    author = UserProfileSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'ingredients',
                  'tags', 'image', 'name',
                  'text', 'cooking_time',)

    def validate(self, data):
        tags = data.get('tags')
        ingredients = data.get('ingredients')

        if not tags:
            raise serializers.ValidationError({'tags': ['Добавьте тег']})

        if len(tags) != len(set(tags)):
            raise serializers.ValidationError({'tags': ['Тег повторяется']})

        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': ['Нет ингредиента']}
            )

        ingredients_set = set()
        for item in ingredients:
            ingredient = get_object_or_404(Ingredient, id=item['id'])

            if ingredient.id in ingredients_set:
                raise serializers.ValidationError(
                    {'ingredients': ['Ингредиент уже есть']}
                )

            amount = int(item['amount'])
            if amount <= 0:
                raise serializers.ValidationError(
                    {'amount': ['Минимальное количество 1']}
                )

            ingredients_set.add(ingredient.id)

        return data

    def create_ingredients_amounts(
            self,
            ingredients: List[Dict],
            recipe: Recipe
    ) -> None:
        ingredient_objects = [
            IngredientInRecipe(
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                recipe=recipe,
                amount=ingredient['amount']
            )
            for ingredient in ingredients
        ]
        IngredientInRecipe.objects.bulk_create(ingredient_objects)

    def update_ingredients_amounts(
            self,
            ingredients: List[Dict],
            recipe: Recipe
    ) -> None:
        ingredient_objects = [
            IngredientInRecipe(
                id=ingredient_in_recipe.id,
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                recipe=recipe,
                amount=ingredient['amount']
            )
            for ingredient, ingredient_in_recipe in
            zip(ingredients, recipe.ingredients.all())
        ]
        IngredientInRecipe.objects.bulk_update(
            ingredient_objects,
            ['ingredient', 'amount']
        )

    def create(self, validated_data: Dict) -> Recipe:
        tags: List[int] = validated_data.pop('tags')
        ingredients: List[Dict] = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients_amounts(recipe=recipe, ingredients=ingredients)
        return recipe

    def update(self, instance: Recipe, validated_data: Dict) -> Recipe:
        tags: List[int] = validated_data.pop('tags')
        ingredients: List[Dict] = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        self.update_ingredients_amounts(
            recipe=instance,
            ingredients=ingredients
        )
        instance.save()
        return instance

    def to_representation(self, instance: Recipe) -> Dict:
        request = self.context.get('request')
        context = {'request': request}
        return RecipeReadSerializer(instance, context=context).data


class RecipeShortSerializer(serializers.ModelSerializer):
    """
    Сериализатор для короткой информации о рецепте.

    Атрибуты:
        name: название рецепта.
        cooking_time: время приготовления рецепта в минутах.

    """

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = fields


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор ингредиента.

    Атрибуты::
        id: уникальный идентификатор ингредиента.
        name: название ингредиента.
        measurement_unit: единица измерения ингредиента.

    """

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)
        read_only_fields = fields


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
