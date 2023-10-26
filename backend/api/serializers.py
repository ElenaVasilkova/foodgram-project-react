from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer as UserHandleSerializer
from rest_framework import serializers, validators

from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingList, Tag)

from users.models import Subscribe

from .imagefield import Base64ImageField

User = get_user_model()


class UserSerializer(UserHandleSerializer):
    """
    Сериализатор для обработки данных о пользователях.
    """
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def create(self, validated_data):
        """Создает нового пользователя."""
        user = User.objects.create_user(**validated_data)
        return user

    def get_is_subscribed(self, author):
        """
        Проверка подписки.
        """
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscribe.objects.filter(
            user=user, author=author).exists()


class ChangePasswordSerializer(serializers.Serializer):
    """
    Сериализатор для изменения пароля.
    """
    new_password = serializers.CharField(
        label='Новый пароль')
    current_password = serializers.CharField(
        label='Текущий пароль')

    def validate_current_password(self, current_password):
        user = self.context['request'].user
        if not authenticate(
                username=user.email,
                password=current_password):
            raise serializers.ValidationError(
                'Не удается войти в систему, '
                'проверьте учетныу данные.',
                code='authorization')
        return current_password

    def validate_new_password(self, new_password):
        validators.validate_password(new_password)
        return new_password

    def create(self, validated_data):
        user = self.context['request'].user
        password = make_password(
            validated_data.get('new_password'))
        user.password = password
        user.save()
        return validated_data


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с подписками пользователей."""
    id = serializers.IntegerField(source='author.id')
    email = serializers.EmailField(source='author.email')
    username = serializers.CharField(source='author.username')
    first_name = serializers.CharField(source='author.first_name')
    last_name = serializers.CharField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )
        read_only_fields = (
            'is_subscribed',
            'recipes_count'
        )

    def validate(self, data):
        """Проверка данных на уровне сериализатора."""
        user_id = data['user_id']
        author_id = data['author_id']
        if user_id == author_id:
            raise serializers.ValidationError({
                'errors': 'Ошибка подписки! Нельзя подписаться на самого себя.'
            })
        if Subscribe.objects.filter(user=user_id,
                                    author=author_id).exists():
            raise serializers.ValidationError({
                'errors': 'Ошибка подписки! Нельзя подписаться повторно.'
            })
        data['user'] = get_object_or_404(User, id=user_id)
        data['author'] = get_object_or_404(User, id=author_id)
        return data

    def get_is_subscribed(self, obj):
        """Проверка подписки."""
        return Subscribe.objects.filter(
            user=obj.user, author=obj.author).exists()

    def get_recipes(self, obj):
        """Получение рецептов автора."""
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit')
        recipes = Recipe.objects.filter(author=obj.author)
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        serializer = FavoriteSubscribeSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        """Подсчет рецептов автора."""
        return Recipe.objects.filter(author=obj.author).count()


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ингредиентов."""
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']
        read_only_fields = ['id', 'name', 'measurement_unit']


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода тегов."""
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для записи ингредиента и количества в рецепт."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')
        validators = [
            validators.UniqueTogetherValidator(
                queryset=IngredientInRecipe.objects.all(),
                fields=('ingredient', 'recipe'),
            )
        ]


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецепта."""
    tags = TagSerializer(read_only=True, many=True)
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    cooking_time = serializers.IntegerField()
    ingredients = IngredientInRecipeSerializer(
        many=True, read_only=True,
        source='ingredient_in_recipe'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart')

    @staticmethod
    def __create_ingredients(recipe, ingredients):
        """Создание ингредиентов в промежуточной таблице."""
        IngredientInRecipe.objects.bulk_create(
            [IngredientInRecipe(recipe=recipe,
             ingredient_id=ingredient.get('id'),
             amount=ingredient.get('amount'))
             for ingredient in ingredients])

    def create(self, validated_data):
        """Создание рецепта."""
        image = validated_data.pop('image')
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(image=image, **validated_data)
        recipe.tags.set(tags)
        self.__create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        """Обновление рецепта."""
        instance.tags.clear()
        instance.tags.set(validated_data.pop('tags'))
        IngredientInRecipe.objects.filter(recipe=instance).delete()
        self.__create_ingredients(
            recipe=instance,
            ingredients=validated_data.pop('ingredients')
        )
        super().update(instance, validated_data)
        return instance

    def to_internal_value(self, data):
        ingredients = data.pop('ingredients')
        tags = data.pop('tags')
        data = super().to_internal_value(data)
        data['tags'] = tags
        data['ingredients'] = ingredients
        return data

    def get_is_favorited(self, obj):
        """Проверка рецепта в избранном."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(recipe=obj, user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        """Проверка списка покупок."""
        user = self.context.get('request').user
        if not user or user.is_anonymous:
            return False
        return ShoppingList.objects.filter(recipe=obj,
                                           user=user).exists()

    def validate(self, data):
        """Проверка данных на уровне сериализатора."""
        ingredients = data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                'Добавьте минимум один ингредиент для рецепта.'
            )
        added_ingredients = []
        for ingredient in ingredients:
            if int(ingredient['amount']) <= 0:
                raise serializers.ValidationError(
                    'Количество ингредиента с id {0} должно '
                    'быть целым и больше 0.'.format(ingredient['id'])
                )
            if ingredient['id'] in added_ingredients:
                raise serializers.ValidationError(
                    'Такой ингридиент уже добавлен.'
                )
            added_ingredients.append(ingredient['id'])
        tags = data.get('tags')
        if len(tags) > len(set(tags)):
            raise serializers.ValidationError('Тег уже используется.')
        cooking_time = float(data.get('cooking_time'))
        if cooking_time < 1:
            raise serializers.ValidationError(
                'Время приготовления должно быть не меньше 1 минуты.')
        data['ingredients'] = ingredients
        data['tags'] = tags
        return data


class FavoriteSubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор для избранного и подписок."""
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
        read_only_fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
