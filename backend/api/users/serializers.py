from djoser.serializers import UserSerializer, UserCreateSerializer
from users.models import User, Follow
from rest_framework import serializers
from django.contrib.auth.validators import UnicodeUsernameValidator
from users.validators import validate_username


class FoodgramUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, data):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=user,
            author=data.id
        ).exists()


class FoodgramUserCreateSerializer(UserCreateSerializer):

    username = serializers.CharField(
        max_length=150,
        required=True,
        validators=[UnicodeUsernameValidator(), validate_username]
    )
    email = serializers.EmailField(
        max_length=254,
        required=True,
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )

    extra_kwargs = {'password': {'write_only': True}}
