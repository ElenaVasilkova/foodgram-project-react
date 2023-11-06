from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from recipes.models import Favorite, Ingredient, Recipe, ShoppingList, Tag
from rest_framework import filters, mixins, serializers, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from users.models import Subscribe

from .creatinglist import collect_shopping_cart
from .filters import IngredientFilter, RecipeFilter
from .pagination import LimitPageNumberPagination
from .permissions import IsAdminUserOrReadOnly, IsOwnerOrReadOnly
from .serializers import (FavoriteSubscribeSerializer, IngredientSerializer,
                          RecipeSerializer, SubscribeSerializer, TagSerializer,
                          UserSerializer)

User = get_user_model()


@api_view(['post'])
def set_password(request):
    """Функция-обработчик для эндпоинта /users/set_password/.
        Позволяет пользователям изменить пароль.
        """
    serializer = UserSerializer(
        data=request.data,
        context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(
            {'message': 'Пароль изменен!'},
            status=status.HTTP_201_CREATED)
    return Response(
        {'error': 'Неверный пароль!'},
        status=status.HTTP_400_BAD_REQUEST)


class CustomUserViewSet(DjoserUserViewSet):
    """Вьюсет для работы с пользователями"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    search_fields = ('username', 'email')

    def get_permissions(self):
        if self.action in ['me']:
            return (IsAuthenticated(),)
        return (AllowAny(),)


class SubscribePostDeleteViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с подписками"""
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    search_fields = ('username', 'email')
    pagination_class = LimitPageNumberPagination
    permission_classes = (IsOwnerOrReadOnly,)
    http_method_names = ['post', 'delete']

    def create(self, request, author_id):
        user = request.user
        author = get_object_or_404(User, id=author_id)

        serializer = SubscribeSerializer(
            author,
            data=request.data,
            context={'request': request})
        serializer.is_valid(raise_exception=True)
        if user == author:
            return Response({
                'errors': 'Нельзя подписаться на самого себя'
            }, status=status.HTTP_400_BAD_REQUEST)

        if Subscribe.objects.filter(user=user, author=author).exists():
            return Response({
                'errors': 'Вы уже подписаны на данного пользователя'
            }, status=status.HTTP_400_BAD_REQUEST)
        Subscribe.objects.create(user=user, author=author)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)

    def delete(self, request, author_id):
        user = request.user
        author = get_object_or_404(User, id=author_id)
        SubscribeSerializer(
            author,
            data=request.data,
            context={'request': request})

        if not Subscribe.objects.filter(
            user=user,
            author=author
        ).exists():
            raise serializers.ValidationError(
                'Нет такой подписки'
            )
        subscription = get_object_or_404(
            Subscribe,
            user=user,
            author=author
        )
        subscription.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscribeListViewSet(mixins.ListModelMixin,
                           viewsets.GenericViewSet):
    """Вьюсет для работы с подписками"""
    queryset = Subscribe.objects.all()
    serializer_class = SubscribeSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    search_fields = ('username', 'email')
    pagination_class = LimitPageNumberPagination
    permission_classes = (IsOwnerOrReadOnly,)
    http_method_names = ['get', 'head']

    def list(self, request):
        """Функция-обработчик для эндпоинта /users/subscriptions/.
        Просмотр подписок ползователя."""
        user = request.user
        user_subscribing = User.objects.filter(
            subscribing__user=user
        )
        page = self.paginate_queryset(user_subscribing)
        serializer = SubscribeSerializer(
            page, context={'request': request}, many=True
        )
        return self.get_paginated_response(serializer.data)


class TagsViewSet(ReadOnlyModelViewSet):
    """Вьюсет для работы с тегами."""
    queryset = Tag.objects.all()
    permission_classes = (IsAdminUserOrReadOnly,)
    serializer_class = TagSerializer
    pagination_class = None


class IngredientsViewSet(ReadOnlyModelViewSet):
    """Вьюсет для работы с ингредиентами."""
    queryset = Ingredient.objects.all()
    permission_classes = (IsAdminUserOrReadOnly,)
    serializer_class = IngredientSerializer
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)
    pagination_class = None


class RecipesViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с рецептами."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsOwnerOrReadOnly, IsAdminUserOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user,)


class FavoriteRecipeViewSet(RecipesViewSet):
    """Вьюсет для списка избранного."""
    queryset = Recipe.objects.all()
    serializer_class = FavoriteSubscribeSerializer
    http_method_names = ['post', 'delete']
    permission_classes = (IsOwnerOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user,)

    def create(self, request, recipe_id):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        serializer = FavoriteSubscribeSerializer(
            recipe, data=request.data,
            context={
                'request': request,
                'action_name': 'favorite'
            }
        )
        serializer.is_valid(raise_exception=True)
        Favorite.objects.create(user=user, recipe=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        serializer = FavoriteSubscribeSerializer(
            recipe, data=request.data,
            context={
                'request': request,
                'action_name': 'favorite'
            }
        )
        serializer.is_valid(raise_exception=True)
        Favorite.objects.filter(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingcartViewSet(RecipesViewSet):
    """Список ингредиентов из рецептов."""
    queryset = Recipe.objects.all()
    serializer_class = FavoriteSubscribeSerializer
    pagination_class = LimitPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsOwnerOrReadOnly,)
    http_method_names = ['post', 'delete']

    def create(self, request, recipe_id):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        serializer = FavoriteSubscribeSerializer(
            recipe, data=request.data,
            context={
                'request': request,
                'action_name': 'shopping_cart'
            }
        )
        serializer.is_valid(raise_exception=True)
        ShoppingList.objects.create(user=user, recipe=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        obj = ShoppingList.objects.filter(user=user, recipe=recipe)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Рецепт уже удален!'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['GET'],
            permission_classes=(IsOwnerOrReadOnly,))
    def download_shopping_cart(self, request):
        """Функция-обработчик для эндпоинта
        /recipes/<id>/download_shopping_cart/.
        Позволяет пользователям скачать список покупок."""
        user = request.user
        if not user.shopping_cart.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return collect_shopping_cart(request)


class ShoppingcartListViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = FavoriteSubscribeSerializer
    filterset_class = RecipeFilter
    http_method_names = ['get', 'head']

    def list(self, request):
        user = request.user
        if not user.shopping_cart.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return collect_shopping_cart(request)
