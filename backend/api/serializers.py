from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.serializers import CharField, IntegerField, ModelSerializer
from rest_framework.validators import UniqueValidator

from api.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                        ShoppingCart, Tag)
from users.serializers import CustomUserSerializer


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
            'name': {'required': False},
            'slug': {'required': False},
            'color': {'required': False}
            }


class IngredientSerializer(ModelSerializer):
    """Серилайзер для модели Ingredient."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        extra_kwargs = {
            'name': {'required': False},
            'measurement_unit': {'required': False}
            }


class FavoriteSerializer(ModelSerializer):
    """Серилайзер для модели Favorite."""

    id = IntegerField(source='recipe.id')
    name = CharField(source='recipe.name')
    image = Base64ImageField(source='recipe.image')
    cooking_time = IntegerField(source='recipe.cooking_time')

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'cooking_time')


class IngredientRepresentationSerializer(serializers.ModelSerializer):
    """Общий вывод ингредиентов по Get запросу."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        fields = '__all__'
        model = IngredientInRecipe


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели IngredientInRecipe для
    обработки Path, Delete, Post запросов.
    """

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), validators=[
            UniqueValidator(queryset=Ingredient.objects.all())
        ]
    )
    amount = serializers.IntegerField(min_value=0)

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')


class RecipeListSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели Recipe с ограниченным набором полей и
    типом разрешения: Чтение.
    Предназначен для метода to_representation основного
    сериализатора: RecipeSerializer.
    """

    tags = TagSerializer(
        many=True, read_only=True
    )
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_ingredients(self, obj):
        """Метод получения списка ингредиентов."""

        queryset = IngredientInRecipe.objects.filter(recipe=obj)
        return IngredientRepresentationSerializer(queryset, many=True).data

    def get_is_favorited(self, obj):
        """Метод проверки на добавление рецепта в избранное."""

        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        """Метод проверки добавления рецепта в корзину."""

        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe=obj).exists()


class RecipeRepresentationSerializer(serializers.ModelSerializer):
    """Сериализатор модели Recipe на чтение."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image',
                  'cooking_time')


class RecipeSerializer(serializers.ModelSerializer):
    """
    Основной сериализатор для модели Recipe.
    Данные проверяются перед добавлением с помощью валидатора.
    Реализованы методы: Создания, Удаления, Обновления рецептов.
    """

    ingredients = IngredientInRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
        )
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(min_value=0)

    class Meta:
        fields = '__all__'
        read_only_fields = ('author',)
        model = Recipe

    def validate(self, validated_data):
        """
        Метод реализации валидатора.
        Входные данные проверяются на соответствие условиям.
        На выходе проверенные данные.
        """

        ingredients = validated_data.get('ingredients')
        ingredients_list = []
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            if ingredient_id in ingredients_list:
                raise serializers.ValidationError({
                    'ingredients': 'Такой ингредиент уже есть в рецепте.'
                })
            ingredients_list.append(ingredient_id)
            amount = ingredient['amount']
            if int(amount) <= 0:
                raise serializers.ValidationError({
                    'amount': 'Количество не может быть нулевым.'
                })

        tags = validated_data.get('tags')
        if not tags:
            raise serializers.ValidationError({
                'tags': 'Не задан tag.'
            })
        tags_list = []
        for tag in tags:
            if tag in tags_list:
                raise serializers.ValidationError({
                    'tags': 'Такой tag уже существует.'
                })
            tags_list.append(tag)

        cooking_time = validated_data.get('cooking_time')
        if int(cooking_time) <= 0:
            raise serializers.ValidationError({
                'cooking_time': 'Время не может быть нулевым.'
            })
        return validated_data

    def create_ingredients(self, ingredients, recipe):
        """Метод создания ингредиента."""

        create_ingredient = [
            IngredientInRecipe(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
                )
            for ingredient in ingredients
            ]
        IngredientInRecipe.objects.bulk_create(create_ingredient)

    def create_tags(self, tags, recipe):
        """Метод создания тега."""

        for tag in tags:
            recipe.tags.add(tag)

    def create(self, validated_data):
        """Метод создания рецепта."""

        author = validated_data.pop('author')
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.create_tags(tags, recipe)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def to_representation(self, instance):
        """Метод прудставления рецептов по Get запросу. На чтение."""

        request = self.context.get('request')
        context = {'request': request}
        return RecipeListSerializer(
            instance, context=context).data

    def update(self, instance, validated_data):
        """Метод обновления рецепта."""

        instance.tags.clear()
        IngredientInRecipe.objects.filter(recipe=instance).all().delete()
        self.create_tags(validated_data.pop('tags'), instance)
        self.create_ingredients(validated_data.pop('ingredients'), instance)
        return super().update(instance, validated_data)
