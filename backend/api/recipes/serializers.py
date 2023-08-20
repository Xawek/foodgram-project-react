from rest_framework.serializers import (
    ModelSerializer,
    SerializerMethodField,
    IntegerField,
    PrimaryKeyRelatedField
)
from recipes.models import (
    Tag,
    Ingredient,
    Recipe,
    IngredientInRecipe,
    Favorite,
)
from api.users.serializers import FoodgramUserSerializer
from drf_extra_fields.fields import Base64ImageField


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
    image = Base64ImageField()
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


class RecSerializer(ModelSerializer):
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
        return RecSerializer(
            recipe,
            context={
                'request': self.context.get('request'),
            }
        ).data
