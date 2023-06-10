from django.contrib.auth import get_user_model

from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework.fields import SerializerMethodField


User = get_user_model()


class UserProfileSerializer(UserSerializer):
    """
    Сериализатор профиля пользователя.

    Атрибуты:
        is_subscribed (SerializerMethodField): поле, указывающее,
        подписан ли текущий пользователь на автора.

    Методы:
        get_is_subscribed(obj: User) -> bool: возвращает True,
        если текущий пользователь подписан на автора, иначе False.

    """

    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj: User) -> bool:
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.subscriber.filter(author=obj).exists()


class UserProfileCreateSerializer(UserCreateSerializer):
    """
    Сериализатор для создания пользователя.

    """

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')
