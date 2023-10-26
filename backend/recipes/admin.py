from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                     ShoppingList, Tag)

EMPTY_STRING: str = '-empty-'

admin.site.site_header = 'Site administration Foodgram'


class RecipeIngredientsAdmin(admin.StackedInline):
    model = IngredientInRecipe
    autocomplete_fields = ('ingredient',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientsAdmin,)
    list_display = (
        'author',
        'name',
        'text',
        'get_favorite_count'
    )
    list_editable = ('name',)
    list_filter = ('author', 'name', 'tags',)
    search_fields = (
        'name',
        'cooking_time',
        'author__username',
        'ingredients__name'
    )
    empty_value_display = EMPTY_STRING

    @admin.display(description='Электронная почта автора')
    def get_author(self, obj):
        return obj.author.email

    @admin.display(description='Теги')
    def get_tags(self, obj):
        return (', '.join(str(tag) for tag in obj.tags.all()))

    @admin.display(description='Ингредиенты')
    def get_ingredients(self, obj):
        return '\n '.join([
            f'{item["ingredient__name"]} - {item["amount"]}'
            f' {item["ingredient__measurement_unit"]}.'
            for item in obj.recipes.values(
                'ingredient__name',
                'amount',
                'ingredient__measurement_unit'
            )
        ])

    @admin.display(description='В избранном')
    def get_favorite_count(self, obj):
        """Подсчитывает сколько раз рецепт добавлен в избранное."""
        return obj.favorites.count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = (
        'name',
        'color',
        'slug'
    )
    list_editable = (
        'slug',
    )
    list_filter = (
        'name',
        'slug',
    )
    search_fields = (
        'name',
        'slug'
    )
    empty_value_display = EMPTY_STRING


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit'
    )
    search_fields = (
        'name',
        'measurement_unit'
    )
    empty_value_display = EMPTY_STRING


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    ordering = ('user',)
    search_fields = (
        'recipe',
        'user'
    )
    list_filter = ('recipe',)
    search_fields = ('recipe',)
    empty_value_display = EMPTY_STRING


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    ordering = ('user',)
    search_fields = (
        'recipe',
        'user'
    )
    list_filter = ('recipe',)
    search_fields = ('recipe',)
    empty_value_display = EMPTY_STRING
