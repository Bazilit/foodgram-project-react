from django.urls import include, path
from rest_framework.routers import DefaultRouter
from api.views import TagViewSet, IngredientViewSet, RecipeViewSet

app_name = 'api'

router = DefaultRouter()
router.register('ingredients', IngredientViewSet)
router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet, basename='recipes')


urlpatterns = (
    path('', include(router.urls)),
)
