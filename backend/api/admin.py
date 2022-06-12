from django.contrib import admin
from api.models import Recipe, Favorite, ShoppingCart, Tag, Ingredient


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('author', 'name', 'cooking_time')
    list_filter = ('author', 'name')


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user','recipe')
    list_filter = ('user','recipe')


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_filter = ('user','recipe')


class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color')
    list_filter = ('name',)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)