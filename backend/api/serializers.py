from rest_framework.serializers import ModelSerializer, CharField, SerializerMethodField, IntegerField
from api.models import Tag, Ingredient, IngredientInRecipe, Recipe, Favorite
from users.serializers import CustomUserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import RegexValidator


class TagSerializer(ModelSerializer):
    """Серилайзер для модели Tag."""

    slug = serializers.SlugField(
        max_length=200,
        unique=True,
        validators=[
            RegexValidator(
                regex='^[-a-zA-Z0-9_]+$',
                message='Недопустимый символ в slug.',
                ),
            ]
        )

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
        extra_kwargs = {
            'id': {'required': True},
        }


class IngredientSerializer(ModelSerializer):
    """Серилайзер для модели Ingredient."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        extra_kwargs = {
            'name': {'required': True},
            'measurement_unit': {'required': True},
        }


class IngredientInRecipeSerializer(ModelSerializer):
    """Серилайзер для модели IngredientInRecipe."""

    name = CharField(source='ingredient.name')
    measurement_unit = CharField(source='ingredient.measurement_unit')

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit')
        extra_kwargs = {
            'name': {'required': True},
            'measurement_unit': {'required': True},
        }


class RecipeSerializer(ModelSerializer):
    """Серилайзер для модели Recipe."""

    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientInRecipeSerializer(many=True, read_only=True)
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited', 'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time')
        extra_kwargs = {
            'tags': {'required': True},
            'author': {'required': True},
            'is_favorited': {'required': True},
            'is_in_shopping_cart': {'required': True},
            'name': {'required': True},
            'image': {'required': True},
            'text': {'required': True},
            'cooking_time': {'required': True},

        }
    
    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Recipe.objects.filter(favorites__user=user, id=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Recipe.objects.filter(shopping_carts__user=user, id=obj.id).exists()


class FavoriteSerializer(ModelSerializer):
    """Серилайзер для модели Favorite."""

    id = IntegerField(source='recipe.id')
    name = CharField(source='recipe.name')
    image = Base64ImageField(source='recipe.image')
    cooking_time = IntegerField(source='recipe.cooking_time')

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'cooking_time')


class ShoppingCartSerializer(ModelSerializer):
    """Серилайзер для модели ShoppingCart."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')