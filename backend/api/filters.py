from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter

from recipes.models import Recipe


class IngredientFilter(SearchFilter):
    """
    Фильтр для Ингредиента.
    """
    search_param = 'name'


class RecipeFilter(filters.FilterSet):
    """
    Фильтр для Рецепта.
    """
    class Meta:
        model = Recipe
        fields = (
            'author',
            'tags')

    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(
        field_name='is_favorited',
        method='get_filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='is_in_shopping_cart',
        method='get_filter_is_in_shopping_cart')

    def get_filter_is_favorited(self, queryset, name, value):
        """Фильтр для избранного"""
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def get_filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтр для списка покупок"""
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset
