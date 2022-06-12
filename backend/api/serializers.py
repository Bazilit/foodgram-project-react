from rest_framework.serializers import ModelSerializer, CharField, SerializerMethodField, IntegerField
from api.models import Tag, Ingredient, IngredientInRecipe, Recipe, Favorite
from users.serializers import CustomUserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueValidator


class TagSerializer(ModelSerializer):
    """Серилайзер для модели Tag."""

    slug = serializers.SlugField(
        max_length=200,
        validators=[
            UniqueValidator(
                message='Данный tag уже существует.',
                queryset=Tag.objects.all()
            )
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
    

    def create(self, validated_data):
        request = self.context.get('request')
        ingredients = self.initial_data.get('ingredients')
        tags_data = self.initial_data.get('tags')
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.tags.set(tags_data)
        for ingredient in ingredients:
            amount = ingredient.get('amount')
            ingredient_creating = Ingredient.get(pk=ingredient.get('id'))
            IngredientInRecipe.objects.bulk_create([recipe, ingredient_creating, amount])
        recipe.save()
        return recipe
    

    def update(self, instance, validated_data):
        ingredients = self.initial_data.get('ingredients')
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)
        instance.tags.clear()
        tags_data = self.initial_data.get('tags')
        instance.tags.set(tags_data)
        IngredientInRecipe.objects.filter(recipe=instance).all().delete()
        for ingredient in ingredients:
            IngredientInRecipe.objects.bulk_create([instance, ingredient.get('id'), ingredient.get('amount')])
        instance.save()
        return instance


class FavoriteSerializer(ModelSerializer):
    """Серилайзер для модели Favorite."""

    id = IntegerField(source='recipe.id')
    name = CharField(source='recipe.name')
    image = Base64ImageField(source='recipe.image')
    cooking_time = IntegerField(source='recipe.cooking_time')

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'cooking_time')
