from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.pagination import FoodgramPagination
from api.recipes.serializers import FollowUserSerializer
from users.models import Follow, User

from .serializers import FoodgramUserSerializer


class FoodgramUsersViewSet(UserViewSet):

    queryset = User.objects.all()
    serializer_class = FoodgramUserSerializer
    permission_classes = (AllowAny, )
    pagination_class = FoodgramPagination

    @action(
        permission_classes=(IsAuthenticated,),
        methods=['POST', 'DELETE'],
        url_path='subscribe',
        detail=True,
    )
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        user = request.user
        if request.method == 'POST':
            if author == user:
                return Response(
                    {'errors': 'Нельзя подписаться на себя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            set_follow = Follow(user=user, author=author)
            set_follow.save()
            serializer = FollowUserSerializer(
                author, context={'request': request},)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            author = get_object_or_404(User, id=id)
            user = request.user
            unfollowing = get_object_or_404(
                Follow,
                user=user,
                author=author
            )
            unfollowing.delete()
            return Response(
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        permission_classes=(IsAuthenticated,),
        methods=['GET'],
        url_path='subscriptions',
        detail=False,
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(
            following__user=request.user
        )
        page = self.paginate_queryset(queryset)
        serializer = FollowUserSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
