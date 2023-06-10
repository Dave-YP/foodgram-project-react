from recipes.models import Ingredient, IngredientInRecipe
from rest_framework import serializers
from rest_framework.fields import IntegerField


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

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError('Минимальное количество 1')
        return value
