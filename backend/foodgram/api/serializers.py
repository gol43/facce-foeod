from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from drf_extra_fields.fields import Base64ImageField
from users.serializers import FavoriteRecipesSerializer, CustomUserSerializer
from recipes.models import (Ingredient, Tag, Recipe,
                            RecipeIngredient, ShoppingCart,
                            RecipeTag, Favorite)


class IngredientSerializer(serializers.ModelSerializer):
    """Банально ингредиенты"""

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Достаём филды ингредиента и кол-во для показа"""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = '__all__'


class AddIngredientRecipeSerializer(serializers.ModelSerializer):
    """Связь ингредиента ччерез кол-во и рецепт через айди"""
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ['id',
                  'amount']


class TagSerializer(serializers.ModelSerializer):
    """Банально теги"""
    class Meta:
        model = Tag
        fields = '__all__'


class RecipeTagSerializer(serializers.ModelSerializer):
    """Связь тега и рецепта"""
    id = serializers.ReadOnlyField(source='tag.id')
    name = serializers.ReadOnlyField(source='tag.name')
    color = serializers.ReadOnlyField(source='tag.color')
    slug = serializers.ReadOnlyField(source='tag.slug')

    class Meta:
        model = RecipeTag
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    """Банально рецепты"""
    author = CustomUserSerializer(read_only=True, required=False)
    ingredients = serializers.SerializerMethodField(required=False)
    tags = serializers.SerializerMethodField(required=False)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart'
        ]

    def get_ingredients(self, obj):
        ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return RecipeIngredientSerializer(ingredients, many=True).data

    def get_tags(self, obj):
        tags = RecipeTag.objects.filter(recipe=obj)
        return RecipeTagSerializer(tags, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        try:
            return Favorite.objects.filter(
                user=request.user, recipe_id=obj.id
            ).exists()
        except Exception as e:
            # Обработка ошибки
            raise ValidationError("Ошибка при проверке избранного: " + str(e),
                                  code='server_error')

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        try:
            return ShoppingCart.objects.filter(
                user=request.user, recipe_id=obj.id
            ).exists()
        except Exception as e:
            # Обработка ошибки
            raise ValidationError(
                "Ошибка при проверке корзины покупок: " + str(e),
                code='server_error')


class CreateRecipeSerializer(serializers.ModelSerializer):
    """create/update для рецептов"""
    author = CustomUserSerializer(read_only=True, required=False)
    ingredients = AddIngredientRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        exclude = ["pub_date", ]

    def create_ingredients(self, ingredients, recipe):
        recipe_ingredients = []
        for ingredient_data in ingredients:
            ingredient_id = ingredient_data.get('id')
            amount = ingredient_data.get('amount')
            ingredient, created = Ingredient.objects.get_or_create(
                id=ingredient_id
            )
            recipe_ingredient = RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient,
                amount=amount
            )
            recipe_ingredients.append(recipe_ingredient)
        RecipeIngredient.objects.bulk_create(recipe_ingredients)

    def create(self, validated_data):
        tags = validated_data.get('tags')
        if not tags:
            raise ValidationError("Необходимо выбрать хотя бы один тег.")
        ingredients_data = validated_data.pop('ingredients', [])
        author = validated_data.pop('author', None)
        if author is None:
            author = self.context.get('request').user
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients_data, recipe)
        return recipe

    def update(self, instance, validated_data):
        instance.ingredients.clear()
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            for ingredient_data in ingredients:
                ingredient, created = Ingredient.objects.get_or_create(
                    id=ingredient_data.get('id'))
                RecipeIngredient.objects.create(
                    recipe=instance,
                    ingredient=ingredient,
                    amount=ingredient_data.get('amount')
                )
        if 'tags' in validated_data:
            instance.tags.set(validated_data.pop('tags'))

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeSerializer(instance, context={
            'request': self.context.get('request')
        }).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Банально список покупок"""

    class Meta:
        model = ShoppingCart
        fields = ['user',
                  'recipe']

    def to_representation(self, instance):
        return FavoriteRecipesSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data
