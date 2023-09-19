from django.core.validators import MinValueValidator
from django.db import models
from colorfield.fields import ColorField
from users.models import User


class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    measurement_unit = models.CharField(max_length=200)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'Ингредиент: {self.name}'


class Tag(models.Model):
    name = models.CharField(unique=True, max_length=200)
    color = ColorField(max_length=7)
    slug = models.SlugField(unique=True, max_length=200)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f'Тег: {self.name}'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes')
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag',
        related_name='recipes',
        blank=False)
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes')
    text = models.TextField(help_text='Описание рецепта')
    name = models.CharField(
        help_text='Название рецепта',
        max_length=200)
    image = models.ImageField(
        help_text='Фото рецепта',
        upload_to='recipes/images/')
    cooking_time = models.PositiveIntegerField(
        help_text='Время готовки в минутах',
        validators=[MinValueValidator(1)])
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return f'Рецепт: {self.name}'


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_tag')
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,)

    def __str__(self):
        return f'Рецепт: {self.recipe} имеет тег(и) -> {self.tag}'

    class Meta:
        unique_together = ('recipe', 'tag')


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        null=True,
        related_name='recipe_ingredients')
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,)
    amount = models.IntegerField(validators=[MinValueValidator(1)], null=True)

    def __str__(self):
        return f'Рецепт:{self.recipe} имеет ингредиент->{self.ingredient}'

    class Meta:
        unique_together = ('recipe', 'ingredient')


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites')

    def __str__(self):
        return f'{self.user} добавил в избранное "{self.recipe}"'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart')

    def __str__(self):
        return f'{self.user} добавил "{self.recipe}" в список покупок'
