from django.shortcuts import render
from djoser import utils, views
from rest_framework.response import Response
from djoser.serializers import TokenSerializer
from rest_framework import status
from users.models import User, Subscription
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import get_object_or_404
from users.pagination import LimitPageNumberPagination
from users.serializers import SubscriptionSerializer


class CustomUserViewset(views.UserViewSet):
    """Стандартный djoser класс пользователя с добавлением методов управления подписками."""

    pagination_class = LimitPageNumberPagination

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated], url_path='subscriptions', url_name='subscriptions',)
    def subscriptions(self, request):
        """метод запроса подписок."""

        user = request.user
        queryset = Subscription.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
    
    @action(methods=['post', 'delete'], detail=True, permission_classes=[IsAuthenticated], url_path='subscribe', url_name='subscribe',)
    def subscribe(self, request, id=None):
        """Метод управления подписками."""

        if request.method == 'POST':
            user = request.user
            author = get_object_or_404(User, id=id)
            if user == author:
                return Response(
                    {'errors': 'Вы не можете подписаться сами на себя.'},
                    status=status.HTTP_400_BAD_REQUEST)
            if Subscription.objects.filter(user=user, author=author).exists():
                return Response(
                    {'errors': 'Вы уже подписаны на данного пользователя.'},
                    status=status.HTTP_400_BAD_REQUEST)
            follow = Subscription.objects.create(user=user, author=author)
            serializer = SubscriptionSerializer(
                follow, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            user = request.user
            author = get_object_or_404(User, id=id)
            if user == author:
                return Response({
                    'errors': 'Вы не можете отписаться сами от себя.'
                })
            follow = Subscription.objects.filter(user=user, author=author)
            if follow.exists():
                follow.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(serializer.data, {
                'errors': 'Подписка на данного пользователя отменена.'
            })
        return Response(status=status.HTTP_204_NO_CONTENT)