from rest_framework.filters import SearchFilter
from django_filters.rest_framework import FilterSet, filters
from recipes.models import Tag, Recipe
from users.models import User


class IngredientFilters(SearchFilter):
    search_param = 'name'

    def filter_queryset(self, request, queryset, view):
        search_value = request.query_params.get(self.search_param, '')
        if search_value:
            queryset = queryset.filter(
                name__icontains=search_value)
        return queryset


class RecipeFilters(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug',
    )
    author = filters.ModelChoiceFilter(
        queryset=User.objects.all()
    )
    is_favorited = filters.BooleanFilter(
        method='get_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'author',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def get_is_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(
                favorite_recipe__user=self.request.user
            )
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(
                shopping__user=self.request.user
            )
        return queryset
