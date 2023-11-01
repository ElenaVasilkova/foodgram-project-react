from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CustomUserViewSet, IngredientsViewSet, RecipesViewSet,
                    # FavoriteRecipeViewSet,
                    SubscribeListViewSet,
                    # ShoppingcartViewSet,
                    SubscribePostDeleteViewSet, TagsViewSet, set_password)

app_name = 'api'

router = DefaultRouter()
router.register('users', CustomUserViewSet, basename='users')
router.register('recipes', RecipesViewSet, basename='recipes')
router.register('tags', TagsViewSet, basename='tags')
router.register('ingredients', IngredientsViewSet, basename='ingredients')
router.register(r'users/(?P<author_id>\d+)/subscribe',
                SubscribePostDeleteViewSet, basename='subscribe')
# router.register(r'recipes/(?P<recipe_id>\d+)/favorite',
#               FavoriteRecipeViewSet, basename='favorite')
# router.register(r'recipes/(?P<recipe_id>\d+)/shopping_cart',
#                ShoppingcartViewSet, basename='shopping_cart')


urlpatterns = [
    path('users/subscriptions/',
         SubscribeListViewSet.as_view({'get': 'list'}),),
    path('', include(router.urls)),
    path('users/set_password/', set_password, name='set_password'),
    path('auth/', include('djoser.urls.authtoken'), name='auth'),
]
