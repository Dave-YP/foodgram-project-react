from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model

from rest_framework.viewsets import ReadOnlyModelViewSet

from recipes.models import Ingredient
from api.filters import IngredientFilter
from api.permissions import IsAdminOrReadOnly
from api.serializers.ingredient_serializers import IngredientSerializer

User = get_user_model()


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
