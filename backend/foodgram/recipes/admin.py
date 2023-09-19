from django.contrib import admin
from .models import (Ingredient, RecipeIngredient,
                     Tag, Recipe,
                     Favorite, ShoppingCart)
from django.core.exceptions import ValidationError
from django import forms
from django.forms import BaseInlineFormSet


class RecipeIngredientFormset(BaseInlineFormSet):
    def clean(self):
        super().clean()

        # Проверяем, есть ли хотя бы один ингредиент
        has_ingredients = any(
            form.cleaned_data and not form.cleaned_data.get(
                'DELETE') for form in self.forms if form.cleaned_data)
        if not has_ingredients:
            raise ValidationError('Необходимо указать ингредиент для рецепта.')


class RecipeTagFormset(BaseInlineFormSet):
    def clean(self):
        super().clean()

        # Проверяем, есть ли хотя бы один ингредиент
        has_tags = any(
            form.cleaned_data and not form.cleaned_data.get(
                'DELETE') for form in self.forms if form.cleaned_data)
        if not has_tags:
            raise ValidationError('Необходимо указать тег для рецепта.')


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

    def clean_tags(self):
        tags = self.cleaned_data.get('tags')
        tag_set = set()

        for tag in tags:
            if tag in tag_set:
                raise ValidationError('Теги не могут повторяться.')
            tag_set.add(tag)

        return tags


class IngredientAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'measurement_unit']
    list_filter = ("name",)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    min_num = 1
    formset = RecipeIngredientFormset


class TagAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'color', 'slug']


class TagsInline(admin.TabularInline):
    model = Recipe.tags.through
    extra = 1
    min_num = 1
    formset = RecipeTagFormset


class RecipeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'author', 'favorites_count', 'pub_date']
    list_filter = ('name', 'author', 'tags',)
    inlines = (RecipeIngredientInline, TagsInline)
    form = RecipeForm

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
