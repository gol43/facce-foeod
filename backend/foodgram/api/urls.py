from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (IngredinetViewSet, TagViewSet, RecipeViewSet)

app_name = 'api'

router = DefaultRouter()
router.register('ingredients', IngredinetViewSet, basename='ingredients')
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
]