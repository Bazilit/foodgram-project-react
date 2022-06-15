from django.contrib import admin

from api.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                        ShoppingCart, Tag)


class IngredientInline(admin.TabularInline):
    model = IngredientInRecipe


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author',)
    fields = ('name', 'cooking_time', 'author', 'tags', 'text', 'image',)
    search_fields = ('name', 'author',)
    inlines = (IngredientInline,)


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)
    list_filter = ('user', 'recipe',)


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)
    list_filter = ('user', 'recipe',)


class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color',)
    list_filter = ('name',)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
