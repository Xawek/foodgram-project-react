from rest_framework.viewsets import ModelViewSet
from .serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer,
    CreateRecipeSerializer,
    FavoriteSerializer,
)
from recipes.models import (
    Tag,
    Ingredient,
    Recipe,
    Favorite,
    ShoppingCart,
    IngredientInRecipe
)
from api.permissions import IsAdminOrReader, IsAdminOrAuthor
from .fiters import IngredientFilters
from django_filters.rest_framework import DjangoFilterBackend
from api.pagination import FoodgramPagination
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.http import HttpResponse
from django.db.models.aggregates import Sum


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

    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PATCH':
            return CreateRecipeSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        permission_classes=(IsAuthenticated,),
        methods=['POST', 'DELETE'],
        url_path='favorite',
        detail=True,
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            recipe = get_object_or_404(Recipe, id=pk)
            Favorite.objects.create(user=request.user, recipe=recipe,)
            serializer = FavoriteSerializer(recipe)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
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
        permission_classes=(IsAuthenticated,),
        methods=['GET', 'POST', 'DELETE'],
        url_path='shopping_cart',
        detail=True,
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            recipe = get_object_or_404(Recipe, id=pk)
            ShoppingCart.objects.create(user=request.user, recipe=recipe,)
            serializer = FavoriteSerializer(recipe)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
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
        url_path='download_shopping_cart',
        detail=False,
    )
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = IngredientInRecipe.objects.filter(
            recipe__shopping__user=user).values(
            'ingredient__name',
            'ingredient__measurement_unit').annotate(
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
