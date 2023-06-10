from typing import Dict, List
from django.db.models import F, QuerySet
from django.shortcuts import get_object_or_404
from collections import Counter

from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from recipes.models import Ingredient, IngredientInRecipe, Recipe, Tag
from .ingredient_serializers import IngredientInRecipeSerializer
from .tag_serializers import TagSerializer
from .user_serializers import UserProfileSerializer
from recipes.models import Favourite, ShoppingCart


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

    ingredients = SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True, allow_empty=False)
    author = UserProfileSerializer(read_only=True)
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

    ingredients = IngredientInRecipeSerializer(
        many=True,
        required=True,
        allow_empty=False
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=True,
        allow_empty=False
    )

    author = UserProfileSerializer(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'ingredients',
                  'tags', 'image', 'name',
                  'text', 'cooking_time',)

    def validate_ingredients(self, ingredients):
        ingredients_set = set()
        for item in ingredients:
            ingredient = get_object_or_404(Ingredient, id=item['id'])

            if ingredient.id in ingredients_set:
                raise serializers.ValidationError(
                    {'ingredients': ['Ингредиент уже есть']}
                )

            ingredients_set.add(ingredient.id)
        return ingredients

    def validate_tags(self, tags):
        tag_counter = Counter(tags)
        for tag, count in tag_counter.items():
            if count > 1:
                raise serializers.ValidationError(
                    {'tags': [f'Тег {tag} повторяется']}
                )
        return tags

    def validate(self, data):
        data['ingredients'] = self.validate_ingredients(
            data.get('ingredients')
        )
        data['tags'] = self.validate_tags(
            data.get('tags')
        )
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
        IngredientInRecipe.objects.filter(recipe=recipe).delete()

        ingredient_objects = [
            IngredientInRecipe(
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                recipe=recipe,
                amount=ingredient['amount']
            )
            for ingredient in ingredients
        ]
        IngredientInRecipe.objects.bulk_create(ingredient_objects)

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


class FavouriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Favourite.

    """

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = Favourite
        fields = ('user', 'recipe')

    def validate(self, data):
        user = data['user']
        recipe = data['recipe']
        if Favourite.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError('Рецепт уже в избранном.')
        return data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели ShoppingCart.

    """

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def validate(self, data):
        user = data['user']
        recipe = data['recipe']
        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                'Рецепт уже присутствует в списке.')
        return data
