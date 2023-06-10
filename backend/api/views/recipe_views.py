import os
from datetime import datetime
from io import BytesIO

from api.filters import RecipeFilter
from api.pagination import LimitPageNumberPagination
from api.permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from api.serializers.recipe_serializers import (FavouriteSerializer,
                                                RecipeReadSerializer,
                                                RecipeShortSerializer,
                                                RecipeWriteSerializer,
                                                ShoppingCartSerializer)
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import Favourite, IngredientInRecipe, Recipe, ShoppingCart
from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

User = get_user_model()


class RecipeViewSet(ModelViewSet):
    """
    Возвращает список всех рецептов.

    Эндпоинты:
        GET /api/recipes/
        GET /api/recipes/{id}/

    """

    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly | IsAdminOrReadOnly,)
    pagination_class = LimitPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.add_to_favorite(request.user, pk)
        return self.delete_from_favorite(request.user, pk)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        """
        Добавляет или удаляет рецепт из списка покупок пользователя.

        Эндпоинты:
            POST /api/recipes/{id}/shopping_cart/
            DELETE /api/recipes/{id}/shopping_cart/

        """

        if request.method == 'POST':
            return self.add_to_shopping_cart(request.user, pk)
        return self.delete_from_shopping_cart(request.user, pk)

    def add_to_favorite(self, user, pk):
        """
        Добавляет рецепт в список избранных пользователя.

        Эндпоинты:
            POST /api/recipes/{id}/favorite/

        """

        serializer = FavouriteSerializer(
            data={'user': user.id, 'recipe': pk},
            context={'request': self.request}
        )

        serializer.is_valid(raise_exception=True)
        favourite = serializer.save()
        recipe = favourite.recipe
        recipe_serializer = RecipeShortSerializer(recipe)
        return Response(recipe_serializer.data, status=status.HTTP_201_CREATED)

    def delete_from_favorite(self, user, pk):
        """
        Удаляет рецепт из списка избранных пользователя.

        Эндпоинты:
            DELETE /api/recipes/{id}/favorite/

        """

        obj = Favourite.objects.filter(user=user, recipe__id=pk)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def add_to_shopping_cart(self, user, pk):
        """
        Добавляет рецепт в список покупок пользователя.

        Эндпоинты:
            POST /api/recipes/{id}/shopping_cart/

        """

        serializer = ShoppingCartSerializer(
            data={'user': user.id, 'recipe': pk},
            context={'request': self.request}
        )
        serializer.is_valid(raise_exception=True)
        shopping_cart = serializer.save()
        recipe = shopping_cart.recipe
        recipe_serializer = RecipeShortSerializer(recipe)
        return Response(recipe_serializer.data, status=status.HTTP_201_CREATED)

    def delete_from_shopping_cart(self, user, pk):
        """
        Удаляет рецепт из списка покупок пользователя.

        Эндпоинты:
            DELETE /api/recipes/{id}/shopping_cart/

        """

        obj = ShoppingCart.objects.filter(user=user, recipe__id=pk)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """
        Скачивает список покупок пользователя в формате PDF.

        Эндпоинты:
            GET /api/users/download_shopping_cart/

        """

        user = request.user

        if not user.shopping_cart.exists():
            return Response({'errors': ['Нет рецептов в списке покупок.']})

        ingredients = IngredientInRecipe.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))

        today = datetime.today()

        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=landscape(letter))

        # можно указать любой загруженный фрифт из папки fonts
        your_font_path = os.path.join(
            settings.BASE_DIR,
            'fonts',
            'RobotoSlab-LightItalic.ttf'
        )
        pdfmetrics.registerFont(
            TTFont('RobotoSlab-LightItalic', your_font_path)
        )

        c.setFont('RobotoSlab-LightItalic', 16)
        c.drawString(50, 550, f'Список покупок для: {user.get_full_name()}')
        c.drawString(50, 530, f'Дата: {today:%Y-%m-%d}')

        c.setFont('RobotoSlab-LightItalic', 14)
        c.drawString(50, 500, 'Название')
        c.drawString(250, 500, 'Единица измерения')
        c.drawString(450, 500, 'Количество')

        y = 480
        for ingredient in ingredients:
            c.drawString(50, y, ingredient["ingredient__name"])
            c.drawString(450, y, str(ingredient["amount"]))
            c.drawString(250, y, ingredient["ingredient__measurement_unit"])
            y -= 20

        c.showPage()
        c.save()
        buffer.seek(0)

        filename = f'{user.username}_shopping_list.pdf'
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename={filename}'

        return response
