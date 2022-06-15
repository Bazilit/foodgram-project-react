from django.core.validators import MinValueValidator
from django.db import models
from django.utils.datetime_safe import date

from users.models import User


class Tag(models.Model):
    """Модель тэгов рецептов."""

    name = models.CharField(
        verbose_name='Название тэга',
        max_length=200,
        unique=True
        )
    color = models.CharField(
        verbose_name='Цвет тэга',
        help_text='Цвет в формате HEX. Пример: #E26C2D',
        max_length=10,
        unique=True,
        )
    slug = models.SlugField(
        verbose_name='Слаг тэга',
        max_length=200,
        unique=True,
        )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель Ингредиентов."""

    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=200,
        )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=200,
        )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта."""

    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления (в минутах)',
        validators=[
            MinValueValidator(
                1, message='Недопустимое значение (меньше 1 мин).'
                ),
            ],
        )
    text = models.TextField(verbose_name='Описание',)
    name = models.CharField(verbose_name='Название', max_length=200,)
    image = models.ImageField(verbose_name='Изображение', upload_to='images/')
    tags = models.ManyToManyField(
        Tag,
        related_name='recipe',
        verbose_name='Тэги',
        )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        verbose_name='Ингредиенты',
        related_name='recipes',
        )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        db_column='author',
        verbose_name='Автор',
        )
    pub_date = models.DateField(
        default=date.today,
        verbose_name='Дата публикации',
        db_index=True
        )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']


class IngredientInRecipe(models.Model):
    """Модель ингредиентов в рецепте с количеством."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Кол-во',
        validators=[MinValueValidator(1, message='Недопустимое кол-во.')],
        )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
                )
            ]


class Favorite(models.Model):
    """Модель Избранное."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name='Пользователь',
        )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite_user_recipe'
                )
            ]


class ShoppingCart(models.Model):
    """Модель списка покупок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shopping_carts",
        verbose_name='Пользователь',
        )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="shopping_carts",
        verbose_name='Рецепт',
        )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shoppingCart_user_recipe'
                )
            ]
