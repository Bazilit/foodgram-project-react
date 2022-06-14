from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from api.models import (
    Tag, Ingredient,
    Recipe, ShoppingCart,
    Favorite, IngredientInRecipe
    )
from api.serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer,
    FavoriteSerializer
    )
from api.filters import (
    IngredientSearchFilter,
    FavoritedAndshoppingCartAndAuthorAndTagFilter
    )
from api.permissions import IsAdmin, ReadOnly, IsOwner
from api.pagination import LimitPageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.http.response import HttpResponse


class TagViewSet(ReadOnlyModelViewSet):
    """
    Обработка тегов по запросу.
    Права на изменение тегов только у Администратора.
    """

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
    filter_backends = [IngredientSearchFilter, ]
    search_fields = ['^name', ]


class RecipeViewSet(ModelViewSet):
    """
    Обработка запросов, связанных с рецептами.
    Права доступа на изменение: Автор, Администратор.
    """
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitPageNumberPagination
    filter_class = FavoritedAndshoppingCartAndAuthorAndTagFilter
    permission_classes = [IsOwner | IsAdmin | ReadOnly]

    def perform_create(self, serializer):
        """Добавление рецепта."""

        serializer.save(author=self.request.user)

    @action(
        methods=['get'],
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path='download_shopping_cart',
        url_name='download_shopping_cart',
        )
    def download_shopping_cart(self, request):
        """Выгрузка данных о покупке в текстовом формате."""

        shopping_list = {}
        user = request.user
        if not user.shopping_carts.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        ingredients = IngredientInRecipe.objects.filter(
            recipe__shopping_carts__user=user
        ).values('amount', 'ingredient__name', 'ingredient__measurement_unit')
        for ingredient in ingredients:
            amount = ingredient['amount']
            name = ingredient['ingredient__name']
            measurement_unit = ingredient['ingredient__measurement_unit']
            if name not in shopping_list:
                shopping_list[name] = {
                    'measurement_unit': measurement_unit,
                    'amount': amount
                }
            else:
                shopping_list[name]['amount'] += amount
        buy_list = ([f'{item} - {value["amount"]} '
                     f'{value["measurement_unit"]} \n'
                     for item, value in shopping_list.items()])
        response = HttpResponse(buy_list, 'Content-Type: text/plain')
        response['Content-Disposition'] = 'attachment; filename="shoplist.txt"'
        return response

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[IsAuthenticated],
        url_path='shopping_cart',
        url_name='shopping_cart',
        )
    def shopping_cart(self, request, pk=id):
        """Добавление и удаление рецепта из список покупок."""

        if request.method == 'POST':
            return self.add(ShoppingCart, request, pk)
        elif request.method == 'DELETE':
            return self.delete_shopping_cart(request, pk)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[IsAuthenticated],
        url_path='favorite',
        url_name='favorite',
        )
    def favorite(self, request, pk=None):
        """Добавление и удаление рецепта из избранное."""

        if request.method == 'POST':
            return self.add(Favorite, request, pk)
        if request.method == 'DELETE':
            return self.delete_favorite(request, pk)

    def add(self, model, request, pk):
        """Метод добавления объекта."""

        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if model.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {'errors': 'Вы уже ранее добавляли данный рецепт в корзину.'},
                status=status.HTTP_400_BAD_REQUEST
                )
        favorite = model.objects.create(user=user, recipe=recipe)
        serializer = FavoriteSerializer(favorite)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_shopping_cart(self, request, pk=None):
        """метод удаления списка покупок."""

        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        favorites = get_object_or_404(
            ShoppingCart, user=user, recipe=recipe
        )
        favorites.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete_favorite(self, request, pk=None):
        """метод удаления из избранного."""

        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        favorites = get_object_or_404(
            Favorite, user=user, recipe=recipe
        )
        favorites.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
