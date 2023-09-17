from django.contrib import admin
from .models import (Ingredient, RecipeIngredient,
                     Tag, Recipe,
                     Favorite, ShoppingCart)
from django.core.exceptions import ValidationError


class IngredientAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'measurement_unit']
    list_filter = ("name",)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


class TagAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'color', 'slug']


class TagsInline(admin.TabularInline):
    model = Tag.recipes.through
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'author', 'favorites_count', 'pub_date']
    list_filter = ('name', 'author', 'tags',)
    inlines = (RecipeIngredientInline, TagsInline)

    # для обязательности tags в админке
    def clean(self):
        if not self.tag.exists():
            raise ValidationError('У рецепта должен быть хотя бы один тег.')

    @admin.display(description='В избранном')
    def favorites_count(self, obj):
        return obj.favorites.count()


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
