from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from api.models import Tag, Ingredient, Recipe, ShoppingCart, Favorite, IngredientInRecipe
from api.serializers import TagSerializer, IngredientSerializer, RecipeSerializer, FavoriteSerializer
from api.filters import IngredientSearchFilter, FavoritedAndshoppingCartAndAuthorAndTagFilter
from api.permissions import IsAdmin, ReadOnly, IsOwner
from api.pagination import LimitPageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.http.response import HttpResponse
from django.db.models import F, Sum



class TagViewSet(ReadOnlyModelViewSet):
    """Обработка тегов по запросу. Права на изменение тегов только у Администратора."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdmin | ReadOnly]


class IngredientViewSet(ReadOnlyModelViewSet):
    """
    Обработка запросов связанных с игридиентами.
    Права на изменение ингридиентов только у Администратора.
    """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [IsAdmin | ReadOnly]
    filter_backends = [IngredientSearchFilter,]
    search_fields = ['^name',]

class RecipeViewSet(ModelViewSet):
    """
    Обработка запросов, связанных с рецептами.
    Права доступа на изменение: Автор, Администратор.
    """
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitPageNumberPagination
    filter_class = [FavoritedAndshoppingCartAndAuthorAndTagFilter,]
    permission_classes = [IsOwner | IsAdmin | ReadOnly]

    def perform_create(self, serializer):
        """Добавление рецепта."""
        serializer.save(author=self.request.user)
    
    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated], url_path='download_shopping_cart', url_name='download_shopping_cart',)
    def download_shopping_cart(self, request):
        """Выгрузка данных о покупке в текстовом формате."""

        user = request.user
        if not user.shopping_carts.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        ingredients = IngredientInRecipe.objects.filter(
            recipe__in=(user.shopping_carts.values('id'))
        ).values(
            ingredient=F('ingredients__name'),
            measure=F('ingredients__measurement_unit')
        ).annotate(amount=Sum('amount'))
        for ingredient in ingredients:
            shopping_list += (
                f'{ingredient["ingredient"]}: {ingredient["amount"]} {ingredient["measure"]}\n'
            )
        response = HttpResponse(
            shopping_list, content_type='text.txt; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename={shopping_list}'
        return response

    @action(methods=['post', 'delete'], detail=True, permission_classes=[IsAuthenticated], url_path='shopping_cart', url_name='shopping_cart',)
    def shopping_cart(self, request, pk=id):
        """Добавление и удаление рецепта из список покупок."""

        if request.method == 'POST':
            return self.add(ShoppingCart, request.user, pk)
        if request.method == 'DELETE':
            return self.delete(ShoppingCart, request.user, pk)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(methods=['post', 'delete'], detail=True, permission_classes=[IsAuthenticated], url_path='favorite', url_name='favorite',)
    def favorite(self, request, pk=None):
        """Добавление и удаление рецепта из избранное."""

        if request.method == 'POST':
            return self.add(Favorite, request.user, pk)
        if request.method == 'DELETE':
            return self.delete(Favorite, request.user, pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def add(self, model, user, pk):
        """Метод добавления объекта."""

        recipe = get_object_or_404(Recipe, id=pk)
        if model.objects.filter(user=user, recipe=recipe).exists():
            return Response({'errors': 'Вы уже ранее добавляли данный рецепт в корзину.'}, status=status.HTTP_400_BAD_REQUEST)
        favorite = model.objects.create(user=user, recipe=recipe)
        serializer = FavoriteSerializer(favorite)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, model, user, pk):
        """Метод удаления объекта."""

        favorite = get_object_or_404(model, user=user, recipe__id=pk)
        if favorite.exists():
            favorite.delete()
            return Response(f'Рецепт {favorite.recipe} удален из вашей корзины.', status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Рецепт уже удален'}, status=status.HTTP_400_BAD_REQUEST)
