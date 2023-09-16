from django.contrib.auth import get_user_model
from rest_framework import serializers
from recipes.models import Recipe

User = get_user_model()


# Изначально нашёл djoser.serializer UserSerializer and UserCreateSerializer
# Но решил, что set_password, который шифрует пароли, подойдёт лучше,
# ввиду своей компактности
class CustomUserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания пользователя"""
    password = serializers.CharField(write_only=True)  # Добавляем поле пароля

    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class CustomUserSerializer(serializers.ModelSerializer):
    """ Сериализатор пользователя"""
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribed']

    def get_is_subscribed(self, obj: User) -> bool:
        user = self.context.get("request").user
        if user.is_anonymous or (user == obj):
            return False
        return user.follower.filter(author=obj).exists()


class FavoriteRecipesSerializer(serializers.ModelSerializer):
    """Сериализатор избранных рецептов"""
    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class SubscribeSerializer(CustomUserSerializer):
    """Сериализатор для получения подписок"""
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta():
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes_count', 'recipes']
        read_only_fields = ('email', 'username', 'first_name', 'last_name',
                            'is_subscribed', 'recipes_count', 'recipes')

    def get_is_subscribed(*args) -> bool:
        return True

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    def get_recipes(self, obj):
        # узнаём параметры запроса
        request = self.context.get('request')
        # получаем int значение recipes_limit из запроса клиента
        limit = request.GET.get('recipes_limit')
        # recipes = related_name у author в модели Recipe
        recipes = obj.recipes.all()
        # Здесь обрабатываем случаи отсутствия и None limit
        if limit:
            # и достаём первые условно 5 рецептов
            recipes = recipes[: int(limit)]
        serializer = FavoriteRecipesSerializer(recipes, many=True,
                                               read_only=True)
        return serializer.data
