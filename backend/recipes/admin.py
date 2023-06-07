from django.contrib import admin

from .models import Favourite, Ingredient, IngredientInRecipe
from .models import Recipe, ShoppingCart, Tag


class IngredientInRecipeInline(admin.TabularInline):
    """
    Встроенный класс администратора
    для модели IngredientInRecipe.

    """

    model = IngredientInRecipe
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """
    Класс администратора для модели Recipe.

    """

    list_display = ('name', 'author',)
    list_filter = ('author', 'name', 'tags',)
    inlines = [IngredientInRecipeInline]
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """
    Класс администратора для модели Ingredient.

    """

    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Класс администратора для модели Tag.

    """

    list_display = ('name', 'color', 'slug',)
    empty_value_display = '-пусто-'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """
    Класс администратора для модели ShoppingCart.

    """

    list_display = ('user', 'recipe',)
    empty_value_display = '-пусто-'


@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    """
    Класс администратора для модели Favourite.

    """

    list_display = ('user', 'recipe',)


@admin.register(IngredientInRecipe)
class IngredientInRecipe(admin.ModelAdmin):
    """
    Класс администратора для модели IngredientInRecipe.

    """

    list_display = ('recipe', 'ingredient', 'amount',)
