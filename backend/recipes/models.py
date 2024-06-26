from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from .validators import validate_color

User = get_user_model()


MAX_LEN = 256


class Ingredient(models.Model):
    """Модель ингредиентов для рецепта."""
    name = models.CharField(
        max_length=MAX_LEN,
        verbose_name='Название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=20,
        verbose_name='Единицы измерения'
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}.'


class Tag(models.Model):
    """Модель тегов для рецепта."""
    name = models.CharField(
        max_length=MAX_LEN,
        unique=True,
        verbose_name='Название тега'
    )
    color = models.CharField(
        max_length=50,
        validators=(validate_color,),
        unique=True,
        verbose_name='Цветовой HEX-код'
    )
    slug = models.SlugField(
        unique=True,
        max_length=64,
        verbose_name='Slug'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['-id']

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецептов."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта'
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=100
    )
    image = models.ImageField(
        blank=True,
        null=True,
        upload_to='static/recipe/',
        verbose_name='Картинка'
    )
    text = models.TextField(
        verbose_name='Текстовое описание рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        related_name='recipes',
        verbose_name='Ингридиенты для приготовления блюда'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тег'
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления в минутах',
        validators=[MinValueValidator(
            1, message='Минимальное время приготовления - 1 минута!'),
        ],
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return f'{self.author.email}, {self.name}'


class IngredientInRecipe(models.Model):
    """Модель для привязки количества ингредиента к рецепту"""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_in_recipe',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        null=True,
        on_delete=models.CASCADE,
        verbose_name='К какому ингредиенту относится',
        related_name='ingredient_in_recipe'
    )
    amount = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(
            1, message='Минимальное количество ингридиентов - 1 !'),
        ],
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'Количество ингредиентов'
        verbose_name_plural = 'Количество ингредиента'
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient_in_recipe')
        ]

    def __str__(self) -> str:
        return f'{self.recipe} - {self.ingredient} - {self.amount}'


class RecipeUserList(models.Model):
    """Класс-предок для моделей избранного и листа покупок."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )

    class Meta:
        abstract = True
        ordering = ('user', 'recipe')


class Favorite(RecipeUserList):
    """Модель для добавления рецептов в избранное."""
    class Meta(RecipeUserList.Meta):
        default_related_name = 'favorites'
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_favorite_list_user'
            )
        ]

    def __str__(self):
        return (f'Пользователь @{self.user.username} '
                f'добавил {self.recipe} в избранное.')


class ShoppingList(RecipeUserList):
    """Модель для списка покупок."""
    class Meta(RecipeUserList.Meta):
        default_related_name = 'shopping_cart'
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_shopping_cart_user'
            )
        ]

    def __str__(self):
        return (f'Пользователь {self.user} '
                f'добавил {self.recipe.name} в покупки.')
