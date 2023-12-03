from colorfield import fields
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from users.models import CustomUser


class Tag(models.Model):
    """Модель тегов."""
    name = models.CharField(
        'Название',
        max_length=200,
        unique=True,
        blank=False
    )
    color = fields.ColorField('Цвет', max_length=7, unique=True, blank=False)
    slug = models.SlugField('Слаг', max_length=200, unique=True, blank=False)

    class Meta:
        ordering = ('id', )
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиентов."""
    name = models.CharField('Название', max_length=200, blank=False)
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=200,
        blank=False
    )

    class Meta:
        ordering = ('name', )
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецептов."""
    name = models.CharField('Название', max_length=200, blank=False)
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления, мин.',
        validators=(MinValueValidator(1, message='Минимальное значение 1'), ),
        blank=False
    )
    text = models.TextField('Описание', blank=False)
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        blank=False
    )
    image = models.ImageField('Картинка', upload_to='recipes/', blank=False)
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег',
        blank=False
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        through_fields=('recipe', 'ingredient'),
        verbose_name='Список ингредиентов',
        blank=False
    )

    class Meta:
        ordering = ('-id', )
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name
    
    def clean(self):
        if not self.name:
            raise ValidationError('Название рецепта не может быть пустым!')
        if not self.cooking_time:
            raise ValidationError('Время приготовления не может быть пустым!')
        if not self.text:
            raise ValidationError('Описание рецепта не может быть пустым!')
        if not self.author:
            raise ValidationError('Автор рецепта не может быть пустым!')
        if not self.image:
            raise ValidationError('Картинка рецепта не может быть пустой!')
        if not self.tags.exists():
            raise ValidationError('Теги рецепта не могут быть пустыми!')
        if not self.ingredients.exists():
            raise ValidationError(
                'Список ингредиентов рецепта не может быть пустым!'
            )
        

class RecipeIngredient(models.Model):
    """
    Модель, которая связывает ингредиенты и рецепты и добавляет новое поле
    amount.
    """
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipe_ingredient'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='recipe_ingredient'
    )
    amount = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(1, message='Минимальное значение 1'), ),
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'

    def __str__(self):
        return (f'{self.ingredient} - {self.amount} '
                f'{self.ingredient.measurement_unit}')


class AbstractModel(models.Model):
    """
    Абстрактная модель, которая связывает пользователя с каким-либо объектом.
    Запись related_name='%(class)s' означает, что связь между пользователем
    и объектом будет иметь динамическое имя, основанное на имени класса.
    В случае с ShoppingCart - это будет shoppingcart, в случае с Favorite -
    favorite.
    """
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='%(class)s'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='%(class)s'
    )

    class Meta:
        abstract = True


class ShoppingCart(AbstractModel):
    """Модель, которая связывает пользователя и покупки (список покупок)."""

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'

    def __str__(self):
        return f'Рецепт {self.recipe} в корзине у пользователя {self.user}'


class Favorite(AbstractModel):
    """Модель, которая связывает пользователя и рецепты (избранные рецепты)."""

    class Meta:
        ordering = ('-id', )
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return f'Рецепт {self.recipe} в избранном у пользователя {self.user}'


class Subscription(models.Model):
    """
    Модель, которая связывает пользователя и автора рецепта (модель подписок).
    """
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='following'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (models.UniqueConstraint(
            fields=('user', 'author'),
            name='unique_subscription'
        ), )

    def __str__(self):
        return f'Пользователь {self.user} подписан на автора {self.author}'

    def clean(self):
        if self.user == self.author:
            raise ValidationError(
                'Невозможно подписаться на самого себя!'
            )
