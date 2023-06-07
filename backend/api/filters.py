from django.contrib.auth import get_user_model

from django_filters.rest_framework import filters, FilterSet

from recipes.models import Ingredient, Recipe, Tag

User = get_user_model()


class RecipeFilter(FilterSet):
    """
    Класс RecipeFilter определяет фильтр для модели Recipe
    по тегу, автору, избранным рецептам и наличии в списке покупок.
    Использует методы get_is_favorited и get_is_in_shopping_cart
    для фильтрации избранного и списка покупок.

    """

    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )

    is_favorited = filters.BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author',)

    def get_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset


class IngredientFilter(FilterSet):
    """
    Класс IngredientFilter определяет фильтр по названию
    ингредиентов для модели Ingredient. Использует метод istartswith
    для поиска по частичному совпадению с заданным именем.

    """

    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)