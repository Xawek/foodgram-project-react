from api.pagination import FoodgramPagination
from api.permissions import IsAdminOrAuthor, IsAdminOrReader
from django.db.models.aggregates import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag)
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .fiters import IngredientFilters, RecipeFilters
from .serializers import (CreateRecipeSerializer, FavoriteSerializer,
                          IngredientSerializer, RecipeSerializer,
                          TagSerializer)


class TagViewSet(ModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = (IsAdminOrReader, )
    pagination_class = None


class IngredientViewSet(ModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    permission_classes = (IsAdminOrReader, )
    filter_backends = (IngredientFilters, )
    pagination_class = None


class RecipeViewSet(ModelViewSet):

    queryset = Recipe.objects.all()
    permission_classes = (IsAdminOrAuthor, )
    pagination_class = FoodgramPagination
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilters

    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PATCH':
            return CreateRecipeSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        permission_classes=(IsAuthenticated, ),
        methods=['POST', 'DELETE'],
        detail=True,
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            recipe = get_object_or_404(Recipe, id=pk)
            serializer = FavoriteSerializer(recipe)
            if not Favorite.objects.filter(
                    user=request.user, recipe=recipe,).exists():
                Favorite.objects.create(user=request.user, recipe=recipe,)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            return Response(
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.method == 'DELETE':
            recipe = get_object_or_404(Recipe, id=pk)
            favorite_for_removre = Favorite.objects.filter(
                user=request.user,
                recipe=recipe
            )
            if favorite_for_removre.exists():
                favorite_for_removre.delete()
                return Response(
                    {'detail': 'Рецепт успешно удален'},
                    status=status.HTTP_204_NO_CONTENT
                )
        return Response(
            {'errors': 'Ошибка запроса'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        permission_classes=(IsAuthenticated, ),
        methods=['POST', 'DELETE'],
        detail=True,
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            recipe = get_object_or_404(Recipe, id=pk)
            serializer = FavoriteSerializer(recipe)
            if not ShoppingCart.objects.filter(
                    user=request.user, recipe=recipe,).exists():
                ShoppingCart.objects.create(user=request.user, recipe=recipe,)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            return Response(
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.method == 'DELETE':
            recipe = get_object_or_404(Recipe, id=pk)
            favorite_for_removre = ShoppingCart.objects.filter(
                user=request.user,
                recipe=recipe
            )
            if favorite_for_removre.exists():
                favorite_for_removre.delete()
                return Response(
                    {'detail': 'Рецепт успешно удален'},
                    status=status.HTTP_204_NO_CONTENT
                )
        return Response(
            {'errors': 'Ошибка запроса'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        permission_classes=(IsAuthenticated,),
        methods=['GET'],
        detail=False,
    )
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = IngredientInRecipe.objects.filter(
            recipe__shopping__user=user).values(
            'ingredient__name',
            'ingredient__measurement_unit').order_by(
            'ingredient__name').annotate(
            amount=Sum('amount')
        )
        data = []
        for ingredient in ingredients:
            data.append(
                f'{ingredient["ingredient__name"]} - '
                f'{ingredient["amount"]} '
                f'{ingredient["ingredient__measurement_unit"]}'
            )
        content = 'Список покупок:\n\n' + '\n'.join(data)
        filename = 'shop.txt'
        request = HttpResponse(content, content_type='text/plain')
        request['Content-Disposition'] = f'attachment; filename={filename}'
        return request
