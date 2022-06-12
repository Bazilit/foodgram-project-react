from rest_framework import serializers
from users.models import Subscription, User
from api.models import Recipe
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework.validators import UniqueValidator
from django.core.validators import RegexValidator
from rest_framework.serializers import ModelSerializer
from drf_extra_fields.fields import Base64ImageField


class CustomUserCreateSerializer(UserCreateSerializer):
    """Серилайзер создания учетной записи пользователя."""

    email = serializers.EmailField(
        validators=[
            UniqueValidator(
                message='Данный адрес уже используется другой учетной записью.',
                queryset=User.objects.all()
            )
        ]
    )
    username = serializers.CharField(
        validators=[
            UniqueValidator(
                message='Данный логин уже существует. Пожалуйста, выберите другой.',
                queryset=User.objects.all()
            ),
        ]
    )

    class Meta:
        model = User
        fields = ('id', 'email', 'username',
                  'first_name', 'last_name', 'password')
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'password': {'required': True},
        }


class CustomUserSerializer(UserSerializer):
    """Серилайзер учетной записи пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')
        extra_kwargs = {
            'username': {'required': True},
        }

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return user.is_authenticated and Subscription.objects.filter(
            user=user, author=obj.id
        ).exists()


class ShoppingCartSerializer(ModelSerializer):
    """Серилайзер для модели ShoppingCart."""
     
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(serializers.ModelSerializer):
    """Серилайзер для подписки."""

    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(
        source='author.username',
        )
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')
        extra_kwargs = {
            'id': {'required': True},
        }

    def get_is_subscribed(self, obj):
        return Subscription.objects.filter(
            user=obj.user, author=obj.author
        ).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = Recipe.objects.filter(author=obj.author)
        if limit:
            queryset = queryset[:int(limit)]
        return ShoppingCartSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()