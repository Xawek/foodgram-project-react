from drf_extra_fields.fields import Base64ImageField
from rest_framework.serializers import (IntegerField, ModelSerializer,
                                        PrimaryKeyRelatedField, ReadOnlyField,
                                        SerializerMethodField, ValidationError)

from api.users.serializers import FoodgramUserSerializer
from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag)
from users.models import User


class FollowUserSerializer(FoodgramUserSerializer):
    recipes = SerializerMethodField(method_name='get_recipes')
    recipes_count = SerializerMethodField(method_name='get_recipes_count')

    class Meta:
        model = User
        fields = (
            'username',
            'id',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, data):
        limit = int(self.context['request'].query_params.get(
            'recipes_limit', default=0)
        )
        recipes = data.recipes.all()
        if limit > 0:
            recipes = recipes[:limit]
        return SmallRecipeSerializer(
            recipes,
            many=True,
        ).data

    def get_recipes_count(self, data):
        return data.recipes.count()


class TagSerializer(ModelSerializer):

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class IngredientSerializer(ModelSerializer):

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class IngredientForRecipeSerializer(ModelSerializer):
    id = SerializerMethodField(
        method_name='get_ingredient_id',
    )
    name = SerializerMethodField(
        method_name='get_ingredient_name'
    )
    measurement_unit = SerializerMethodField(
        method_name='get_ingredient_measure'
    )

    def get_ingredient_id(self, data):
        return data.ingredient.id

    def get_ingredient_name(self, data):
        return data.ingredient.name

    def get_ingredient_measure(self, data):
        return data.ingredient.measurement_unit

    class Meta:
        model = IngredientInRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class RecipeSerializer(ModelSerializer):
    image = ReadOnlyField(source='image.url')
    tags = TagSerializer(
        many=True
    )
    author = FoodgramUserSerializer()
    ingredients = SerializerMethodField(
        method_name='get_ingredients'
    )

    def get_ingredients(self, data):
        ingredients = IngredientForRecipeSerializer(
            IngredientInRecipe.objects.filter(recipe=data), many=True
        )
        return ingredients.data

    is_favorited = SerializerMethodField(
        method_name='get_is_favorited',
    )
    is_in_shopping_cart = SerializerMethodField(
        method_name='get_is_in_shopping_cart',
        read_only=True
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'image',
            'author',
            'ingredients',
            'name',
            'text',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def get_is_favorited(self, recipe):
        request = self.context.get('request')
        user = request.user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(user=user, recipe=recipe).exists()

    def get_is_in_shopping_cart(self, recipe):
        request = self.context.get('request')
        user = request.user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=user, recipe=recipe).exists()


class CreateIngredientForRecipeSerializer(ModelSerializer):
    id = IntegerField()
    amount = IntegerField()

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'amount',
        )


class CreateRecipeSerializer(ModelSerializer):
    image = Base64ImageField()
    tags = PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = CreateIngredientForRecipeSerializer(many=True)

    def validate_tags(self, tags):
        if not tags:
            raise ValidationError(
                'Добавьте тег'
            )
        return tags

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise ValidationError(
                'Добавьте ингредиент'
            )
        ingredients_list = []
        for ingredient_id in ingredients:
            ingredients_list.append(ingredient_id['id'])
        if len(ingredients_list) != len(set(ingredients_list)):
            raise ValidationError('Одинаковые ингредиенты')
        return ingredients

    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        for ingredient_data in ingredients_data:
            ingredient = Ingredient.objects.get(pk=ingredient_data['id'])
            amount = ingredient_data['amount']
            IngredientInRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=amount
            )
        return recipe

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        instance.tags.set(tags_data)
        instance.ingredients.clear()
        for ingredient_data in ingredients_data:
            ingredient = Ingredient.objects.get(pk=ingredient_data['id'])
            amount = ingredient_data['amount']
            IngredientInRecipe.objects.create(
                recipe=instance,
                ingredient=ingredient,
                amount=amount
            )
        return super().update(instance, validated_data)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'image',
            'tags',
            'ingredients',
            'name',
            'text',
            'cooking_time',
        )

    def to_representation(self, recipe):
        return RecipeSerializer(
            recipe,
            context={
                'request': self.context.get('request'),
            }
        ).data


class SmallRecipeSerializer(ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'image',
            'name',
            'cooking_time',
        )


class FavoriteSerializer(ModelSerializer):

    class Meta:
        model = Favorite
        fields = (
            'user',
            'recipe',
        )

    def to_representation(self, recipe):
        return SmallRecipeSerializer(
            recipe,
            context={
                'request': self.context.get('request'),
            }
        ).data
