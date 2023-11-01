from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CustomUserViewSet, FavoriteRecipeViewSet,
                    IngredientsViewSet, RecipesViewSet,
                    ShoppingcartListViewSet, ShoppingcartViewSet,
                    SubscribeListViewSet, SubscribePostDeleteViewSet,
                    TagsViewSet, set_password)

app_name = 'api'

router = DefaultRouter()
router.register(r'users/(?P<author_id>\d+)/subscribe',
                SubscribePostDeleteViewSet, basename='subscribe')
router.register(r'users/subscriptions',
                SubscribeListViewSet, basename='subscribe')
router.register('users', CustomUserViewSet, basename='users')
router.register(r'recipes/(?P<recipe_id>\d+)/favorite',
                FavoriteRecipeViewSet, basename='favorite')
router.register(r'recipes/(?P<recipe_id>\d+)/shopping_cart',
                ShoppingcartViewSet, basename='shopping_cart')
router.register(r'recipes/download_shopping_cart',
                ShoppingcartListViewSet, basename='shopping_cart')
router.register('recipes', RecipesViewSet, basename='recipes')
router.register('tags', TagsViewSet, basename='tags')
router.register('ingredients', IngredientsViewSet, basename='ingredients')


urlpatterns = [
    path('', include(router.urls)),
    path('users/set_password/', set_password, name='set_password'),
    path('auth/', include('djoser.urls.authtoken'), name='auth'),
]
