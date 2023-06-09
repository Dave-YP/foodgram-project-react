from datetime import datetime
from django.conf import settings
from io import BytesIO
import os

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from djoser.views import UserViewSet

from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from recipes.models import Favourite, Ingredient
from recipes.models import IngredientInRecipe, Recipe
from recipes.models import ShoppingCart, Tag
from users.models import Subscription
from .filters import IngredientFilter, RecipeFilter
from .pagination import LimitPageNumberPagination
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .user_serializers import UserProfileSerializer
from .recipe_serializers import RecipeWriteSerializer, RecipeReadSerializer
from .recipe_serializers import RecipeShortSerializer
from .tag_serializers import TagSerializer
from .subscription_serializers import SubscriptionSerializer
from .ingredient_serializers import IngredientSerializer

User = get_user_model()


class UserProfileViewSet(UserViewSet):
    """"
    Класс UserProfileViewSet для работы с профилями пользователей.
    Добавляет дополнительные функции для управления подписками.

    Методы:
        subscribe: обрабатывает POST и DELETE запросы
        для создания и удаления подписок на авторов.
        manage_subscription: метод для создания и удаления подписок.
        subscriptions: возвращает список авторов,
        на которых подписан пользователь.

    Эндпоинты:
        POST /api/users/{id}/subscribe/
        DELETE /api/users/{id}/subscribe/
        GET /api/users/subscriptions/

    """

    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = (AllowAny,)
    pagination_class = LimitPageNumberPagination

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, **kwargs):
        current_user = request.user
        target_author_id = self.kwargs.get('id')
        target_author = get_object_or_404(User, id=target_author_id)

        if request.method == 'POST':
            return self.manage_subscription(
                request,
                current_user,
                target_author,
                action_type='create'
            )

        if request.method == 'DELETE':
            return self.manage_subscription(
                request,
                current_user,
                target_author,
                action_type='delete'
            )

    def manage_subscription(
            self,
            request,
            current_user,
            target_author,
            action_type
    ):
        if action_type == 'create':
            serializer = SubscriptionSerializer(
                target_author,
                data=request.data,
                context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            Subscription.objects.create(
                user=current_user,
                author=target_author
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif action_type == 'delete':
            subscription_instance = get_object_or_404(
                Subscription,
                user=current_user,
                author=target_author
            )
            subscription_instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        current_user = request.user
        queryset = User.objects.filter(subscribing__user=current_user)
        paginated_queryset = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            paginated_queryset,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class IngredientViewSet(ReadOnlyModelViewSet):
    """
    Возвращает список ингредиентов по названию или ингредиента по id.

    Эндпоинты:
        GET /api/ingredients/
        GET /api/ingredients/{id}/

    """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class TagViewSet(ReadOnlyModelViewSet):
    """
    Возвращает список всех тегов или тега по id.

    Эндпоинты:
        GET /api/tags/
        GET /api/tags/{id}/

    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


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
        else:
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
        else:
            return self.delete_from_shopping_cart(request.user, pk)

    def add_to_favorite(self, user, pk):
        """
        Добавляет рецепт в список избранных пользователя.

        Эндпоинты:
            POST /api/recipes/{id}/favorite/

        """

        if Favourite.objects.filter(user=user, recipe__id=pk).exists():
            return Response({'errors': ['Рецепт уже уже в избранном.']})
        recipe = get_object_or_404(Recipe, id=pk)
        Favourite.objects.create(user=user, recipe=recipe)
        serializer = RecipeShortSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_from_favorite(self, user, pk):
        """
        Удаляет рецепт из списка избранных пользователя.

        Эндпоинты:
            DELETE /api/recipes/{id}/favorite/

        """

        obj = Favourite.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': ['Рецепт не найден в избранном.']})

    def add_to_shopping_cart(self, user, pk):
        """
        Добавляет рецепт в список покупок пользователя.

        Эндпоинты:
            POST /api/recipes/{id}/shopping_cart/

        """

        if ShoppingCart.objects.filter(user=user, recipe__id=pk).exists():
            return Response({'errors': ['Рецепт уже присутствует в списке.']})
        recipe = get_object_or_404(Recipe, id=pk)
        ShoppingCart.objects.create(user=user, recipe=recipe)
        serializer = RecipeShortSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_from_shopping_cart(self, user, pk):
        """
        Удаляет рецепт из списка покупок пользователя.

        Эндпоинты:
            DELETE /api/recipes/{id}/shopping_cart/

        """

        obj = ShoppingCart.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': ['Пользователь не имеет рецептов в списке.']}
        )

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
