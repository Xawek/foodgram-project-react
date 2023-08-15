from djoser.views import UserViewSet
from users.models import User
from rest_framework.permissions import AllowAny
from .serializers import FoodgramUserSerializer


class FoodgramUsersViewSet(UserViewSet):

    queryset = User.objects.all()
    serializer_class = FoodgramUserSerializer
    permission_classes = (AllowAny, )
