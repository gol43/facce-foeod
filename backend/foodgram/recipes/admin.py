from django.contrib import admin
from .models import (Ingredient, RecipeIngredient,
                     Tag, Recipe,
                     Favorite, ShoppingCart)
from django.core.exceptions import ValidationError
from django import forms


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = '__all__'

    def clean_ingredients(self):
        ingredients = self.cleaned_data.get('ingredients')
        ingredient_set = set()

        for ingredient in ingredients:
            if ingredient in ingredient_set:
                raise ValidationError('Ингредиенты не могут повторяться.')
            ingredient_set.add(ingredient)

        return ingredients


class IngredientAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'measurement_unit']
    list_filter = ("name",)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    min_num = 1


class TagAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'color', 'slug']


class TagsInline(admin.TabularInline):
    model = Recipe.tags.through
    extra = 1
    min_num = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'author', 'favorites_count', 'pub_date']
    list_filter = ('name', 'author', 'tags',)
    inlines = (RecipeIngredientInline, TagsInline)
    form = RecipeForm

    def save_model(self, request, obj, form, change):
        if not change:
            if not obj.ingredients.exists() or not obj.tags.exists():
                raise ValidationError(
                    'У рецепта должен быть один ингредиент и один тег.')
        super().save_model(request, obj, form, change)

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
