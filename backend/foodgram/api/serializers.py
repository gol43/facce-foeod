from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from users.serializers import FavoriteRecipesSerializer, CustomUserSerializer
from recipes.models import (Ingredient, Tag, Recipe,
                            RecipeIngredient, ShoppingCart,
                            RecipeTag)


class IngredientSerializer(serializers.ModelSerializer):
    """Банально ингредиенты"""

    class Meta:
        model = Ingredient
        fields = ['id',
                  'name',
                  'measurement_unit']


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
        fields = ['id',
                  'name',
                  'color',
                  'slug']


class RecipeTagSerializer(serializers.ModelSerializer):
    """Связь тега и рецепта"""
    id = serializers.ReadOnlyField(source='tag.id')
    name = serializers.ReadOnlyField(source='tag.name')
    color = serializers.ReadOnlyField(source='tag.color')
    slug = serializers.ReadOnlyField(source='tag.slug')

    class Meta:
        model = RecipeTag
        fields = ['id',
                  'name',
                  'color',
                  'slug']


class RecipeSerializer(serializers.ModelSerializer):
    """Банально рецепты"""
    author = CustomUserSerializer(read_only=True, required=False)
    ingredients = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_ingredients(self, obj):
        ingredients = obj.recipe_ingredients.all()
        return RecipeIngredientSerializer(ingredients, many=True).data

    def get_tags(self, obj):
        tags = obj.recipe_tags.all()
        return RecipeTagSerializer(tags, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.favorites.filter(user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.shopping_cart.filter(user=request.user).exists()


class CreateRecipeSerializer(serializers.ModelSerializer):
    """create/update для рецептов"""
    author = CustomUserSerializer(read_only=True, required=False)
    ingredients = AddIngredientRecipeSerializer(many=True, required=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True, required=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        exclude = ["pub_date", ]

    def create_ingredients(self, ingredients, recipe):
        recipe_ing = []
        for ingredient_data in ingredients:
            ingredient, created = Ingredient.objects.get_or_create(
                id=ingredient_data.get('id'))
            recipe_ing.append(RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient,
                amount=ingredient_data.get('amount')
            ))
        RecipeIngredient.objects.bulk_create(recipe_ing)

    def validate(self, data):
        tags = data.get('tags')
        if not tags or len(tags) == 0:
            raise serializers.ValidationError(
                "Необходимо указать хотя бы один тег.")

        return data

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])
        tags = validated_data.pop('tags', [])
        author = validated_data.pop('author', None)
        if author is None:
            author = self.context.get('request').user

        # Проверяем уникальность ингредиентов
        ingredient_ids = set()
        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data.get('id')
            if ingredient_id in ingredient_ids:
                raise serializers.ValidationError(
                    f"Ингредиент с ID {ingredient_id} уже добавлен к рецепту.")
            ingredient_ids.add(ingredient_id)

        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients_data, recipe)
        return recipe

    def update(self, instance, validated_data):
        # Обработка обновления рецепта
        instance.name = validated_data.get('name', instance.name)
        # Добавьте обработку других полей рецепта, которые нужно обновить

        # Обработка обновления ингредиентов
        if 'ingredients' in validated_data:
            ingredients_data = validated_data['ingredients']

            # Проверяем уникальность ингредиентов
            ingredient_ids = set()
            for ingredient_data in ingredients_data:
                ingredient_id = ingredient_data.get('id')
                ingredient_naming = ingredient_data.get('name')
                if ingredient_id in ingredient_ids:
                    raise serializers.ValidationError(
                        f"Ингредиент {ingredient_naming} уже добавлен!!!")
                ingredient_ids.add(ingredient_id)

            instance.ingredients.clear()

            for ingredient_data in ingredients_data:
                ingredient, created = Ingredient.objects.get_or_create(
                    id=ingredient_data.get('id'))
                RecipeIngredient.objects.create(
                    recipe=instance,
                    ingredient=ingredient,
                    amount=ingredient_data.get('amount')
                )

        # Обработка обновления тегов
        if 'tags' in validated_data:
            instance.tags.set(validated_data['tags'])

        instance.save()
        return instance

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
