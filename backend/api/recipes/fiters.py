from rest_framework.filters import SearchFilter


class IngredientFilters(SearchFilter):
    search_param = 'name'
