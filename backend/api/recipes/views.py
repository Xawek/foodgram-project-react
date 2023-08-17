from rest_framework.viewsets import ModelViewSet
from .serializers import TagSerializer, IngredientSerializer
from recipes.models import Tag, Ingredient
from api.permissions import IsAdminOrReader
from .fiters import IngredientFilters


class TagViewSet(ModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = (IsAdminOrReader, )


class IngredientViewSet(ModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    permission_classes = (IsAdminOrReader, )
    filter_backends = (IngredientFilters, )
