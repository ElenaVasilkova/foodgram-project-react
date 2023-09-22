from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from recipes.models import (FavoriteRecipe, Ingredient, Recipe, ShoppingList,
                            Tag)
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from users.models import Subscribe

from .filters import IngredientFilter, RecipeFilter
from .pagination import LimitPageNumberPagination
from .permissions import IsAdminUserOrReadOnly, IsOwnerOrReadOnly
from .serializers import (FavoriteSubscribeSerializer, IngredientSerializer,
                          RecipeSerializer, SubscribeSerializer, TagSerializer,
                          UserSerializer)
from .creatinglist import collect_shopping_list

User = get_user_model()


@api_view(['post'])
def set_password(request):
    """
    Изменить пароль.
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
    """
    Пользователи и подписки.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    search_fields = ('username', 'email')
    permission_classes = (AllowAny,)

    @action(methods=['POST', 'DELETE'], detail=True,)
    def subscribe(self, request, id):
        """
        Подписаться / отписаться.
        """
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            if request.user.id == author.id:
                raise ValueError('Нельзя подписаться на себя самого')
            serializer = SubscribeSerializer(
                Subscribe.objects.create(user=request.user,
                                         author=author),
                context={'request': request})
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if Subscribe.objects.filter(user=request.user,
                                        author=author
                                        ).exists():
                Subscribe.objects.filter(user=request.user,
                                         author=author
                                         ).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'Нельзя отписаться от автора, '
                 'на которго не подписан!'},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(methods=['GET'],
            detail=False,
            permission_classes=(IsAuthenticated, )
            )
    def subscriptions(self, request):
        """
        Получить подписки.
        """
        serializer = SubscribeSerializer(
            self.paginate_queryset(Subscribe.objects.filter(
                                   user=request.user)),
            many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)


class TagsViewSet(ReadOnlyModelViewSet):
    """
    Список тегов.
    """
    queryset = Tag.objects.all()
    permission_classes = (IsAdminUserOrReadOnly,)
    serializer_class = TagSerializer
    pagination_class = None


class IngredientsViewSet(ReadOnlyModelViewSet):
    """
    Список ингридиентов.
    """
    queryset = Ingredient.objects.all()
    permission_classes = (IsAdminUserOrReadOnly,)
    serializer_class = IngredientSerializer
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)
    pagination_class = None


class RecipesViewSet(viewsets.ModelViewSet):
    """
    Список рецептов.
    """
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsOwnerOrReadOnly, )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user,)

    def new_favorite_or_list(self, model, user, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = FavoriteSubscribeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def remove_favorite_or_list(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Рецепт уже удален!'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        """
        Добавить рецепт в избранное или удалить из него.
        """
        if request.method == 'POST':
            return self.new_favorite_or_cart(FavoriteRecipe,
                                             request.user, pk)
        return self.remove_favorite_or_cart(FavoriteRecipe,
                                            request.user, pk)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated])
    def shopping_list(self, request, pk=None):
        """
        Добавить рецепт в список покупок или удалить из него.
        """
        if request.method == 'POST':
            return self.new_favorite_or_cart(ShoppingList, request.user, pk)
        return self.remove_favorite_or_cart(ShoppingList, request.user, pk)

    @action(detail=False, methods=['GET'],
            permission_classes=(IsAuthenticated,))
    def download_shopping_list(self, request):
        """
        Скачать список покупок.
        """
        user = request.user
        if not user.shopping_cart.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return collect_shopping_list(request)
