from django.db.models import F, Sum
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.filters import (FavoritedAndshoppingCartAndAuthorAndTagFilter,
                         IngredientSearchFilter)
from api.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                        ShoppingCart, Tag)
from api.pagination import LimitPageNumberPagination
from api.permissions import IsAdmin, IsOwner, ReadOnly
from api.serializers import (FavoriteSerializer, IngredientSerializer,
                             RecipeSerializer, TagSerializer)


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

        user = request.user
        if not user.shopping_carts.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        ingredients = IngredientInRecipe.objects.filter(
            recipe__shopping_carts__user=user
        ).values('ingredient__name', 'ingredient__measurement_unit').annotate(
            name=F('ingredient__name'),
            unit=F('ingredient__measurement_unit'),
            total_amount=Sum('amount')
            ).order_by('-total_amount')
        buy_list = '\n'.join(
            [
                (
                    f"{ingredient['name']}: "
                    f"{ingredient['total_amount']} "
                    f"{ingredient['unit']}\n"
                    )
                for ingredient in ingredients
                ]
            )
        response = HttpResponse(buy_list, 'Content-Type: text/plain')
        response['Content-Disposition'] = 'attachment; filename="buy_list.txt"'
        return response

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[IsAuthenticated],
        url_path='shopping_cart',
        url_name='shopping_cart',
        )
    def shopping_cart(self, request, pk):
        """Добавление и удаление рецепта из список покупок."""
        return self.metod_delete_create(request, pk, ShoppingCart)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[IsAuthenticated],
        url_path='favorite',
        url_name='favorite',
        )
    def favorite(self, request, pk):
        """Добавление и удаление рецепта из избранное."""
        return self.metod_delete_create(request, pk, Favorite)

    def metod_delete_create(self, request, pk, model):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            creation_model = model.objects.filter(user=user, recipe=recipe)
            if creation_model.exists():
                return Response(
                    {'errors': 'Данный объект уже создан.'},
                    status=status.HTTP_400_BAD_REQUEST
                    )
            favorite = model.objects.create(user=user, recipe=recipe)
            serializer = FavoriteSerializer(favorite)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            delete_model = model.objects.filter(user=user, recipe=recipe)
            if delete_model.exists():
                delete_model.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {
                    'errors': 'Невозможно удалить. '
                              'Данного объекта не существует.'
                    },
                status=status.HTTP_400_BAD_REQUEST
                )
