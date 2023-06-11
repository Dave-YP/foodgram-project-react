from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import slugify

from colorful.fields import RGBColorField

User = get_user_model()


class Tag(models.Model):
    """
    Модель тегов.

    Атрибуты:
        name: название тега (CharField).
        color: цвет тега (RGBColorField).
        slug: уникальный слаг тега (SlugField).

    """

    name = models.CharField(
        verbose_name='Название тега',
        max_length=200,
        unique=True,
        help_text='Введите название тега (максимум 200 символов)'
    )
    color = RGBColorField(
        verbose_name='Цвет тега',
        max_length=7,
        default='#E26C2D',
        unique=True,
        help_text='Выберите цвет тега из предложенных вариантов',
        colors=[
            '#FF0000', '#00FF00', '#0000FF',
            '#FFFF00', '#FF00FF', '#00FFFF',
            '#800080', '#008000', '#800000',
            '#000080', '#FFC0CB',
        ]
    )
    slug = models.SlugField(
        verbose_name='Уникальный слаг',
        max_length=100,
        unique=True,
        help_text='Введите уникальный слаг(максимум 100 символов).'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        slug = slugify(self.slug)
        if (Tag.objects.filter(slug=slug).exists()
                and self.pk != Tag.objects.get(slug=slug).pk):
            raise ValidationError('Указанный слаг уже занят')
        else:
            self.slug = slug

        super().save(*args, **kwargs)


class Ingredient(models.Model):
    """
    Модель ингредиентов.

    Атрибуты:
        name: название ингредиента.
        measurement_unit: единица измерения ингредиента.

    """

    name = models.CharField(
        verbose_name='Название',
        max_length=200,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=200,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    """
    Модель рецептов.

    Атрибуты:
        name: название рецепта.
        tags: список тегов.
        author: автор рецепта.
        ingredients: список ингредиентов.
        cooking_time: время приготовления.
        text: описание рецепта.
        image: фото рецепта.

    """

    name = models.CharField(
        verbose_name='Название',
        max_length=200,
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        related_name='recipes',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='recipes',
        on_delete=models.CASCADE,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        related_name='recipes',
        through='IngredientInRecipe',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления (в минутах)',
        validators=[MinValueValidator(1, message='Минимальное время 1 минута')]
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
        max_length=3000
    )
    image = models.ImageField(
        verbose_name='Загрузить фото',
        upload_to='recipes/'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    """
    Модель связи между ингредиентами и рецептами.

    Атрибуты:
        recipe -- рецепт.
        ingredient -- ингредиент.
        amount -- количество ингредиента.

    """

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='ingredient_list',
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(1, message='Минимальное значение 1')]
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'

    def __str__(self):
        return (
            f'{self.ingredient.name} ({self.ingredient.measurement_unit})'
            f' - {self.amount} '
        )


class Favourite(models.Model):
    """
    Модель для хранения списка избранных рецептов пользователей.

    Атрибуты:
        user: пользователь.
        recipe: рецепт.

    """

    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='favorites',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='favorites',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favourite'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил в избранное {self.recipe}'


class ShoppingCart(models.Model):
    """
    Модель для хранения списка покупок пользователей.

    """

    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='shopping_cart',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='shopping_cart',
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил в список покупок {self.recipe}'
