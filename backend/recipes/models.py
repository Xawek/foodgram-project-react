from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    RegexValidator,
)
from django.db import models

from foodgram.constants import (
    LENGTH_VALUE_FOR_COLOR,
    LENGTH_VALUE_FOR_RECIPE,
    MAX_VALUE_FOR_RECIPE,
    MIN_VALUE_FOR_RECIPE,
)
from users.models import User


class Tag(models.Model):

    name = models.CharField(
        blank=False,
        max_length=LENGTH_VALUE_FOR_RECIPE,
        unique=True,
        verbose_name='Название тега',

    )
    color = models.CharField(
        blank=False,
        max_length=LENGTH_VALUE_FOR_COLOR,
        unique=True,
        verbose_name='Цвет тега',
    )
    slug = models.SlugField(
        blank=False,
        max_length=LENGTH_VALUE_FOR_RECIPE,
        unique=True,
        validators=[RegexValidator('^[-a-zA-Z0-9_]+$')],
        verbose_name='Идентификатор',
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Ingredient(models.Model):
    name = models.CharField(
        max_length=LENGTH_VALUE_FOR_RECIPE,
        verbose_name='Название ингредиента',
    )
    measurement_unit = models.CharField(
        max_length=LENGTH_VALUE_FOR_RECIPE,
        verbose_name='Единица измерения',
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Recipe(models.Model):
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        related_name='recipes',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        through='TagForRecipe',
        related_name='recipes',
        verbose_name='Теги',
    )
    name = models.CharField(
        blank=False,
        max_length=LENGTH_VALUE_FOR_RECIPE,
        verbose_name='Название рецепта',
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(MIN_VALUE_FOR_RECIPE),
            MaxValueValidator(MAX_VALUE_FOR_RECIPE),
        ],
        verbose_name='Время приготовления',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    image = models.ImageField(
        upload_to='recipes/media',
        blank=False,
        verbose_name='Изображение',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class IngredientInRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_recipe',
        verbose_name='Ингредиент',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredient',
        verbose_name='Рецепт',
    )
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(MIN_VALUE_FOR_RECIPE)],
        verbose_name='Количество',
    )

    def __str__(self):
        return self.recipe.name

    class Meta:
        ordering = ['id']
        verbose_name = 'Ингридиент в рецептe'
        verbose_name_plural = 'Ингридиенты в рецептe'


class TagForRecipe(models.Model):
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Тег',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    def __str__(self):
        return self.recipe.name

    class Meta:
        ordering = ['id']
        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецепта'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_user',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
        verbose_name='Рецепт',
    )

    def __str__(self):
        return self.recipe.name

    class Meta:
        ordering = ['id']
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=(
                    'user',
                    'recipe'
                ),
                name='unique_favorite'
            )
        ]


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping',
        verbose_name='Рецепт',
    )

    def __str__(self):
        return self.recipe.name

    class Meta:
        ordering = ['id']
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        constraints = [
            models.UniqueConstraint(
                fields=(
                    'user',
                    'recipe'
                ),
                name='unique_shopping_cart'
            )
        ]
