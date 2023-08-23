from rest_framework.serializers import (
    ModelSerializer,
    SerializerMethodField,
    IntegerField,
    PrimaryKeyRelatedField,
    ReadOnlyField
)
from recipes.models import (
    Tag,
    Ingredient,
    Recipe,
    IngredientInRecipe,
    Favorite,
)
from users.models import User, Follow
from api.users.serializers import FoodgramUserSerializer
from drf_extra_fields.fields import Base64ImageField


class FollowUserSerializer(FoodgramUserSerializer):
    recipes = SerializerMethodField(method_name='get_recipes')
    recipes_count = SerializerMethodField(method_name='get_recipes_count')
    is_subscribed = SerializerMethodField(method_name='get_is_subscribed')
    email = ReadOnlyField()
    first_name = ReadOnlyField()
    last_name = ReadOnlyField()
    username = ReadOnlyField()

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
        limit = self.context['request'].query_params.get('recipes_limit')
        recipes = data.recipes.all()[:(int(limit))]
        return SmallRecipeSerializer(
            recipes,
            many=True,
        ).data

    def get_recipes_count(self, data):
        return data.recipes.count()

    def get_is_subscribed(self, data):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=user,
            author=data.id
        ).exists()


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
        )


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
