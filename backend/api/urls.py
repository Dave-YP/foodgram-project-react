from django.urls import include, path
from rest_framework import routers

from .ingredient_views import IngredientViewSet
from .recipe_views import RecipeViewSet
from .tag_views import TagViewSet
from .user_views import UserProfileViewSet

router = routers.DefaultRouter()
router.register('ingredients', IngredientViewSet, basename='ingredient')
router.register('recipes', RecipeViewSet, basename='recipe')
router.register('tags', TagViewSet, basename='tag')
router.register('users', UserProfileViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
