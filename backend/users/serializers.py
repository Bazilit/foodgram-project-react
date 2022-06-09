from rest_framework import serializers
from users.models import Follow, User
from api.models import Recipe
from api import serializers as api_serializers
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework.validators import UniqueValidator, RegexValidator


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
            RegexValidator(
                regex='^[\w.@+-]+\z',
                message='Недопустимый символ в имени пользователя.',
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
        return user.is_authenticated and Follow.objects.filter(
            user=user, author=obj.id
        ).exists()



class FollowSerializer(serializers.ModelSerializer):
    """Серилайзер для подписки."""

    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(
        source='author.username',
        validators=[
            RegexValidator(
                regex='^[\w.@+-]+\z',
                message='Недопустимый символ в имени пользователя.',
                ),
            ]
        )
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')
        extra_kwargs = {
            'id': {'required': True},
        }

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(
            user=obj.user, author=obj.author
        ).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = Recipe.objects.filter(author=obj.author)
        if limit:
            queryset = queryset[:int(limit)]
        return api_serializers.CropRecipeSerializer(queryset,
                                                    many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()