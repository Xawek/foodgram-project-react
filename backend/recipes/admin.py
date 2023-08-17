from django.contrib import admin

from .models import Tag, Ingredient


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
