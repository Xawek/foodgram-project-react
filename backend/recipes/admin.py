from django.contrib import admin

from .models import Favorite, Ingredient, Recipe, ShoppingCart, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'color',
        'slug',
    )
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit',
    )


class IngredientsInLine(admin.TabularInline):
    model = Recipe.ingredients.through
    extra = 0
    min_num = 1


class TagInLine(admin.TabularInline):
    model = Recipe.tags.through
    extra = 0
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'author',
        'name',
        'text',
        'pub_date',
    )
    search_fields = (
        'author',
        'name',
    )
    inlines = [IngredientsInLine, TagInLine]


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe_name',
    )
    search_fields = (
        'user',
        'recipe__name',
    )

    def recipe_name(self, obj):
        return obj.recipe.name

    recipe_name.short_description = 'Название рецепта'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe_name',
    )
    search_fields = (
        'user',
        'recipe__name',
    )

    def recipe_name(self, obj):
        return obj.recipe.name

    recipe_name.short_description = 'Название рецепта'
