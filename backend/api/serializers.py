from rest_framework.serializers import ModelSerializer, CharField, SerializerMethodField, IntegerField
from api.models import Tag, Ingredient, IngredientInRecipe, Recipe, Favorite, ShoppingCart
from users.serializers import CustomUserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from django.shortcuts import get_object_or_404


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


class IngredientInRecipeSerializer(ModelSerializer):
    """Серилайзер для модели IngredientInRecipe."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')
        validators = [
            UniqueTogetherValidator( 
                queryset=IngredientInRecipe.objects.all(),
                fields=['ingredient', 'recipe']
            )
        ]


class RecipeSerializer(ModelSerializer):
    """Серилайзер для модели Recipe."""

    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = serializers.SerializerMethodField(read_only=True)
    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited', 'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time')

    def get_ingredients(self, obj):
        queryset = IngredientInRecipe.objects.filter(recipe=obj)
        return IngredientInRecipeSerializer(queryset, many=True).data
    
    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(user=request.user,
                                       recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=request.user,
                                       recipe=obj).exists()
    
    def create_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            IngredientInRecipe.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount'),
            )
    
    def get_tags_and_ingredients(self, ingredients, recipe):
        tags = self.initial_data.get('tags')
        for tag_id in tags:
            recipe.tags.add(get_object_or_404(Tag, pk=tag_id))
        for ingredient in ingredients:
            ingredients_amount = IngredientInRecipe.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount')
            )
            ingredients_amount.save()
    
    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        ingredients_set = set()
        for ingredient in ingredients:
            if int(ingredient.get('amount')) <= 0:
                raise serializers.ValidationError(
                    ('Количество ингредиента должно быть больше "0"')
                )
            ingredient_id = ingredient.get('id')
            if ingredient_id in ingredients_set:
                raise serializers.ValidationError(
                    'Дубликат ингредиента в рецепте.'
                )
            ingredients_set.add(ingredient_id)
        data['ingredients'] = ingredients
        if int(self.initial_data.get('cooking_time')) <= 0:
            raise serializers.ValidationError(
                ('Время приготовления не может быть меньше 1.')
            )
        tags = self.initial_data.get('tags')
        if tags is None:
            raise serializers.ValidationError(
                ('Добавьте тег.')
            )
        return data

    def create(self, validated_data):
        image = validated_data.pop('image')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(image=image, **validated_data)
        self.get_tags_and_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        instance.tags.clear()
        ingredients = validated_data.pop('ingredients')
        IngredientInRecipe.objects.filter(recipe=instance).delete()
        self.get_tags_and_ingredients(ingredients, instance)
        if validated_data.get('image') is not None:
            instance.image = validated_data.get('image')
        instance.name = validated_data.get('name')
        instance.text = validated_data.get('text')
        instance.cooking_time = validated_data.get('cooking_time')
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
