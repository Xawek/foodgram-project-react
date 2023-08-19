from django.contrib import admin

from .models import Tag, Ingredient, Recipe


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
    extra = 1


class TagInLine(admin.TabularInline):
    model = Recipe.tags.through
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
            'id',
            'author',
            'name',
            'text',
    )
    search_fields = (
            'author',
            'name',
    )
    inlines = [IngredientsInLine, TagInLine]
