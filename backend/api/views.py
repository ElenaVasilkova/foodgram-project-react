from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from recipes.models import Favorite, Ingredient, Recipe, ShoppingList, Tag
from users.models import Subscribe

from .creatinglist import collect_shopping_cart
from .filters import IngredientFilter, RecipeFilter
from .pagination import LimitPageNumberPagination
from .permissions import (IsAdminUserOrReadOnly, IsSubscribeOnly,
                          IsOwnerOrReadOnly)
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


class UserViewSet(DjoserUserViewSet):
    """Вьюсет для работы с пользователями"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    search_fields = ('username', 'email')
    # permission_classes = (AllowAny,)

    def get_permissions(self):
        if self.action in ['me']:
            return (IsAuthenticated(),)
        return (AllowAny(),)


class SubscribeViewSet(DjoserUserViewSet):
    # queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    search_fields = ('username', 'email')
    pagination_class = LimitPageNumberPagination
    # permission_classes = (AllowAny,)

    def get_permissions(self):
        """Дает доступ к определенным эндпоинтам только аутентифицированным
        пользователям и разрешает метод delete только для своих подписок."""
        if self.request.method == 'DELETE':
            return (IsSubscribeOnly(),)
        if self.action in ['me', 'subscriptions', 'subscribe']:
            return (IsAuthenticated(),)
        return (AllowAny(),)

    @action(methods=['POST', 'DELETE'], detail=True,)
    def subscribe(self, request, id):
        """Функция-обработчик для эндпоинта
        /users/subscriptions/<id>/subscribe/.
        Позволяет пользователям подписываться или отписываться
        от обновлений других пользователей.
        """
        user = request.user
        author = get_object_or_404(User, id=id)
        print(author)

        if request.method == 'POST':
            print(author)
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
            subscribe = Subscribe.objects.create(user=user, author=author),

            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if user == author:
                return Response({
                    'errors': 'Нельзя отписаться от самого себя'
                }, status=status.HTTP_400_BAD_REQUEST)

            subscribe = Subscribe.objects.filter(user=user, author=author),
            if subscribe.exists():
                subscribe.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'Нельзя отписаться от автора, '
                 'на которго не подписан!'},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(methods=['GET'],
            detail=False,
            permission_classes=(IsAuthenticated,)
            )
    def subscriptions(self, request):
        """Функция-обработчик для эндпоинта /users/subscriptions/.
        Просмотр подписок ползователя."""
        user = self.request.user
        user_subscribing = Subscribe.objects.filter(subscribing__user=user)
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
    permission_classes = (IsOwnerOrReadOnly, IsAdminUserOrReadOnly)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user,)

    def new_favorite_or_cart(self, model, user, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = FavoriteSubscribeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def remove_favorite_or_cart(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Рецепт уже удален!'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated,])
    def favorite(self, request, pk=None):
        """Функция-обработчик для эндпоинта /recipes/<id>/favorite/.
        Добавить рецепт в избранное или удалить из него."""
        if request.method == 'POST':
            return self.new_favorite_or_cart(Favorite,
                                             request.user, pk)
        return self.remove_favorite_or_cart(Favorite,
                                            request.user, pk)


class ShoppingcartViewSet(viewsets.ModelViewSet):
    """Список ингредиентов из рецептов."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsOwnerOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user,)

    def new_cart(self, model, user, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = FavoriteSubscribeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def remove_cart(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Рецепт уже удален!'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        """Функция-обработчик для эндпоинта /recipes/<id>/shopping_cart/.
        Добавить рецепт в список покупок или удалить из него."""
        if request.method == 'POST':
            return self.new_favorite_or_list(ShoppingList, request.user, pk)
        return self.remove_favorite_or_list(ShoppingList, request.user, pk)

    @action(detail=False, methods=['GET'],
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        """Функция-обработчик для эндпоинта
        /recipes/<id>/download_shopping_cart/.
        Позволяет пользователям скачать список покупок."""
        user = request.user
        if not user.shopping_cart.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return collect_shopping_cart(request)
