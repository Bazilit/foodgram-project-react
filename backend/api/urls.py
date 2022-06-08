from django.urls import include, path
from rest_framework.routers import DefaultRouter
from api.views import TagViewSet, IngredientSerializer, RecipeViewSet

app_name = 'api'

router = DefaultRouter()
router.register('tags', TagViewSet, 'tags')
router.register('ingredients', IngredientSerializer, 'ingredients')
router.register('recipes', RecipeViewSet, 'recipes')


urlpatterns = (
    path('', include(router.urls)),
)