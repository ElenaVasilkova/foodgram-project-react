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
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(
        field_name='is_favorited',
        method='get_filter_is_favorited')
    is_in_shopping_list = filters.BooleanFilter(
        field_name='is_in_shopping_list',
        method='get_filter_is_in_shopping_list')

    def get_filter_is_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def get_filter_is_in_shopping_list(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping_list__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_list')
