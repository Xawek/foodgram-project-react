from rest_framework.viewsets import ModelViewSet
from .serializers import TagSerializer
from recipes.models import Tag
from api.permissions import IsAdminOrReader


class TagViewSet(ModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = (IsAdminOrReader, )
