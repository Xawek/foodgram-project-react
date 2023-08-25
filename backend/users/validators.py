from rest_framework import serializers


def validate_username(username):
    """Недопустимое названия поля username."""
    invalid_usernames = [
        'set_password',
        'admin',
        'root',
        'api',
        'users',
        'user',
        'subscriptions',
        'subscription',
        'subscribe',
        'recipes',
        'recipe',
        'favorite',
        'shopping_cart',
        'tags',
        'tag',
        'auth',
        'token',
        'login',
        'logout',
        'ingredients',
        'ingredient',
    ]

    if username.lower() in invalid_usernames:
        raise serializers.ValidationError(f'{username} недоступно')
    return username
