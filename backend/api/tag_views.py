from django.contrib.auth import get_user_model

from rest_framework.viewsets import ReadOnlyModelViewSet

from recipes.models import Tag
from .permissions import IsAdminOrReadOnly
from .tag_serializers import TagSerializer

User = get_user_model()


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
