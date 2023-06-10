from api.permissions import IsAdminOrReadOnly
from api.serializers.tag_serializers import TagSerializer
from django.contrib.auth import get_user_model
from recipes.models import Tag
from rest_framework.viewsets import ReadOnlyModelViewSet

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
