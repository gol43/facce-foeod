from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAuthorOrAdminOrReadOnly
from .pagination import LimitPageNumberPagination
from rest_framework.response import Response
from django.http import HttpResponse
from django.db.models import Sum
from datetime import datetime
from rest_framework.permissions import SAFE_METHODS
from .serializers import (
    IngredientSerializer,
    TagSerializer,
    RecipeSerializer,
    CreateRecipeSerializer,
)
from recipes.models import (
    Tag,
    Ingredient,
    Recipe,
    ShoppingCart,
    Favorite,
    RecipeIngredient,
)
from users.serializers import FavoriteRecipesSerializer


class IngredinetViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientFilter,)
    search_fields = ("^name",)
    pagination_class = None


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by("-pub_date")
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    pagination_class = LimitPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return CreateRecipeSerializer

    def append(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            return Response(
                {"errors": "Где-то мы это видели"},
                status=status.HTTP_400_BAD_REQUEST
            )
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = FavoriteRecipesSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def execution(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"errors": "Где-то мы это видели"},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=["post", "delete"])
    def favorite(self, request, pk):
        if request.method == "POST":
            return self.append(Favorite, request.user, pk)
        if request.method == "DELETE":
            return self.execution(Favorite, request.user, pk)

    @action(detail=True, methods=["post", "delete"])
    def shopping_cart(self, request, pk):
        if request.method == "POST":
            return self.append(ShoppingCart, request.user, pk)
        if request.method == "DELETE":
            return self.execution(ShoppingCart, request.user, pk)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        ingredients = (
            RecipeIngredient.objects.filter(
                recipe__shopping_cart__user=request.user)
            .values("ingredient__name", "ingredient__measurement_unit")
            .annotate(amount=Sum("amount"))
        )
        today = datetime.today()
        shopping_list = (
            f"Пользователь: {request.user.username} ({request.user.email})\n"
            f"Дата: {today:%Y-%m-%d}\n\n"
        )
        shopping_list += "\n".join(
            [
                f'- {ingredient["ingredient__name"]} - {ingredient["amount"]} '
                f'{ingredient["ingredient__measurement_unit"]}'
                for ingredient in ingredients
            ]
        )
        filename = f"{request.user}_shopping_list.txt"
        response = HttpResponse(shopping_list, content_type="text/plain")
        response["Content-Disposition"] = f"attachment; filename={filename}"
        return response
