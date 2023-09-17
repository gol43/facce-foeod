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


# Изначально я увиделю в пачке, что кто-то использует source и
# паралельно нашёл статью и про serializersmethodfield и to_representation
# https://pythonist.ru/effektivnoe-ispolzovanie-drf-serializatorov-v-django/
# И ещё в вебинаре говорилось про использование нескольких классов
# сериализаторов, чтобы было всё более понятно.
# Здесь также создаётся связь рецепта и ингредиента
class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Достаём филды ингредиента и кол-во для показа"""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ['id',
                  'name',
                  'measurement_unit',
                  'amount']


# Важный класс. Прочитав redoc, можно понять, что ингредиенты связываются
# с рецептами по кол-ву и айди соответственно
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


# Тут я спицально также добавил этот класс для метода
# get_tags, потому-что на главной странице у рецептов
# не показывались теги
# Этот сериализатор используется для связи тегов с рецептами.
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
        # Получаем доступ к текущему запросу через
        # запрос (request) содержит информацию о текущем пользователе.
        request = self.context.get('request')
        # Здесь проверяем на анонимность, ведь они не могут подписываться
        # И будет возвращаться то самое булевое значение(FALSE)
        if not request or request.user.is_anonymous:
            return False
        # А если усё оке, то метод этотт делает проверку наличия
        # связи между пользовотелем и рецептом в таблице favorites.
        return obj.favorites.filter(user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.shopping_cart.filter(user=request.user).exists()


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

    # Этот метод я честно говоря увидел в пачке. Но могу его объяснить
    def create_ingredients(self, ingredients, recipe):
        # Этот цикл проходит по списку ингредиентов, предоставленных клиентом
        for ingredient_data in ingredients:
            # Это уже идёт проверка на наличие ингредиента с указанным айди
            # Если всё, ок, то идём дальше, а если нет, то or_create,
            # создаём этот самый ингредиент.
            ingredient, created = Ingredient.objects.get_or_create(
                id=ingredient_data.get('id'))
            # Эта строка создает запись в базе данных,
            # связывающую ингредиент с рецептом.
            # Она создает экземпляр RecipeIngredient
            RecipeIngredient.objects.create(
                # Это рецепт, с которым будет связан ингредиент
                recipe=recipe,
                # Это ингредиент, который будет связан с рецептом
                ingredient=ingredient,
                # Это количество ингредиента, указанное клиентом
                amount=ingredient_data.get('amount')
            )

    def create(self, validated_data):
        # Здесь мы просто достаём данные из списков из
        # validated_data, а если его  нет,
        # то добавляем объекты в пустой список.
        # p.s. я пробовал и через --get-- и через --add--
        #      но почему-то ничего не получалось.
        ingredients_data = validated_data.pop('ingredients', [])
        tags = validated_data.pop('tags', [])
        # Здесь в приницпе также идёт доп проверка на
        # анонима и аутеризованного пользователя.
        # у меня в одном из docker compose up, получалось
        # зайти на страницу создания без авторизации просто
        author = validated_data.pop('author', None)
        if author is None:
            author = self.context.get('request').user
        # здесь мы создаём объект рецепта.
        recipe = Recipe.objects.create(author=author, **validated_data)
        # Вообще изначально делал также доп.  метод create_tags
        # и потом через .pop() создавал эти теги, но всё в той же пачке
        # увидел этот вариант записи всего в одну строчку.
        # Здесь мы устанавливаем через set() связь тегов,
        # которые представлены в модели Recipe
        recipe.tags.set(tags)
        self.create_ingredients(ingredients_data, recipe)
        return recipe

    # Здесь по сути то же самое, только изначально
    # мы удалаем изменяемые объекты
    def update(self, instance, validated_data):
        instance.ingredients.clear()  # Очищаем связи с ингредиентами
        # unstance содержит в себе уже имющиеся в бд объекты
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

    # здесь to_representation просто вызывает другой
    # сериализатор RecipeSerializer,чтобы представить
    # уже имеющиеся объекты модели в бд
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
