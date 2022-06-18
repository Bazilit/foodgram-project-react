from django.contrib import admin

from api.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                        ShoppingCart, Tag)


class IngredientInline(admin.TabularInline):
    model = IngredientInRecipe


class RecipeAdmin(admin.ModelAdmin):
    inlines = (IngredientInline,)
    list_display = ('name', 'author', 'cooking_time',
                    'id', 'count_favorite', 'pub_date',)
    search_fields = ('name', 'author', 'tags')
    list_filter = ('name', 'author', 'tags')
    empty_value_display = 'пусто'

    def count_favorite(self, obj):
        return Favorite.objects.filter(recipe=obj).count()


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user',)
    list_filter = ('user',)
    empty_value_display = 'пусто'


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'id')
    search_fields = ('user',)
    list_filter = ('user',)
    empty_value_display = 'пусто'


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = 'пусто'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = 'пусто'


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
