from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientsViewSet, RecipesViewSet, ShoppingcartViewSet,
                    SubscribeViewSet, TagsViewSet, UserViewSet, set_password)

app_name = 'api'

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('recipes', RecipesViewSet, basename='recipes')
router.register('tags', TagsViewSet, basename='tags')
router.register('ingredients', IngredientsViewSet, basename='ingredients')
router.register(r'recipes/(?P<recipe_id>\d+)/shopping_cart',
                ShoppingcartViewSet, basename='shopping_cart')
router.register(r'users/subscriptions', SubscribeViewSet,
                basename='subscriptions')
router.register(r'users/(?P<author_id>\d+)/subscribe', SubscribeViewSet,
                basename='subscribe')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('users/set_password/', set_password, name='set_password'),
    path('auth/', include('djoser.urls.authtoken'), name='auth'),
]
