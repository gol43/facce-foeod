from django_filters.rest_framework import FilterSet, filters
from rest_framework.filters import SearchFilter

from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(SearchFilter):
    search_param = 'name'

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    # Страница доступна всем пользователям. Доступна фильтрация по избранному,
    # автору, списку покупок и тегам. Взято из редок
    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited')
    author = filters.CharFilter(field_name="author__id")
    # Можно было бы использовать NumberField, через
    # '1' и '0',  ну булево значечние интуитивно понятнее
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart')
    tags = filters.ModelMultipleChoiceFilter(field_name='tags__slug',
                                             to_field_name='slug',
                                             queryset=Tag.objects.all(),)

    # queryset = набор рецептов
    # name = Поле, по которому как раз таки идёт фильтрация
    # value = то самое булево значение, где True=фильтровать..
    # favorites и shopping_cart взяты из related_name моделей
    def filter_is_favorited(self, queryset, name, value):
        client = self.request.user
        if value and client.is_authenticated:
            # Если оба условия истинны, то мы фильтруем queryset,
            # чтобы вернуть только те рецепты, которые
            # добавлены в избранное client.
            # Юзаем связь favorites__user, чтобы проверить,
            # есть ли запись об избранности рецепта этим пользователем.
            return queryset.filter(favorites__user=client)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        client = self.request.user
        if value and client.is_authenticated:
            return queryset.filter(shopping_cart__user=client)
        return queryset

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'author', 'is_in_shopping_cart', 'tags')
