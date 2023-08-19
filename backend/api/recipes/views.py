from rest_framework.viewsets import ModelViewSet
from .serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer,
    CreateRecipeSerializer,
)
from recipes.models import Tag, Ingredient, Recipe
from api.permissions import IsAdminOrReader, IsAdminOrAuthor
from .fiters import IngredientFilters
from django_filters.rest_framework import DjangoFilterBackend
from api.pagination import FoodgramPagination


class TagViewSet(ModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = (IsAdminOrReader, )


class IngredientViewSet(ModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    permission_classes = (IsAdminOrReader, )
    filter_backends = (IngredientFilters, )


class RecipeViewSet(ModelViewSet):

    queryset = Recipe.objects.all()
    permission_classes = (IsAdminOrAuthor, )
    pagination_class = FoodgramPagination
    filter_backends = (DjangoFilterBackend, )

    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PATCH':
            return CreateRecipeSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
