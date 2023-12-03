from django_filters.rest_framework import FilterSet, filters
from recipes.models import Ingredient, Recipe, Tag
from users.models import CustomUser


class IngredientFilter(FilterSet):
    """Поиск ингредиента по начальным символам."""
    name = filters.CharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ('name', )


class RecipeFilter(FilterSet):
    """
    Поиск рецепта по автору и тегу, по нахождению в избранном и списке покупок.
    """
    author = filters.ModelChoiceFilter(queryset=CustomUser.objects.all())
    tags = filters.ModelMultipleChoiceFilter(
        label='Тег',
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug'
    )
    is_favorited = filters.BooleanFilter(
        label='В избранном',
        method='get_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        label='В списке покупок',
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    # Фильтр по избранному
    def get_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value:
            return queryset.filter(favorite__user=user)
        return queryset

    # Фильтр по списку покупок
    def get_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value:
            return queryset.filter(shoppingcart__user=user)
        return queryset
