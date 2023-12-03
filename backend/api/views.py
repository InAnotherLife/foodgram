from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Subscription, Tag)
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from users.models import CustomUser

from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomPagination
from .permissions import IsAdminOrAuthorOrReadOnly
from .serializers import (IngredientSerializer, RecipeCreateUpdateSerializer,
                          RecipeFavoriteSerializer, RecipeSerializer,
                          SubscriptionSerializer, TagSerializer)
from .utils import AbstractCreateDeleteMixin


class CustomUserViewSet(AbstractCreateDeleteMixin, UserViewSet):
    """Вьюсет кастомного пользователя."""
    queryset = CustomUser.objects.all()
    permission_classes = (IsAdminOrAuthorOrReadOnly, )
    pagination_class = CustomPagination
    http_method_names = ('get', 'post', 'patch', 'delete')

    # Получение подписчиков пользователя
    @action(
        methods=('get', ),
        detail=False
    )
    def subscriptions(self, request):
        queryset = CustomUser.objects.filter(following__user=request.user)
        obj = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            obj,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    # Подписка на автора рецепта или отписка от автора рецепта
    @action(
        methods=('post', 'delete'),
        detail=True
    )
    def subscribe(self, request, **kwargs):
        author_id = self.kwargs.get('id')
        return self.perform_action(
            Subscription,
            CustomUser,
            SubscriptionSerializer,
            request,
            author_id,
            'author',
            'Вы уже пописаны на этого автора!',
            'Вы не подписаны на этого автора!'
        )


class TagViewSet(ModelViewSet):
    """Вьюсет тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrAuthorOrReadOnly, )


class IngredientViewSet(ModelViewSet):
    """Вьюсет ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrAuthorOrReadOnly, )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = IngredientFilter


class RecipeViewSet(AbstractCreateDeleteMixin, ModelViewSet):
    """Вьюсет рецептов."""
    queryset = Recipe.objects.all()
    permission_classes = (IsAdminOrAuthorOrReadOnly, )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter
    pagination_class = CustomPagination
    http_method_names = ('get', 'post', 'patch', 'delete')

    # Получение всех объектов модели Recipe с предварительной выборкой
    # связанных моделей recipe_ingredient__ingredient и tags для
    # оптимизации запросов к БД за счет сокращения количества обращений к ней
    def get_queryset(self):
        return Recipe.objects.prefetch_related(
            'recipe_ingredient__ingredient', 'tags'
        ).all()

    # Если создается новый рецепт или обновляется существующий, то возвращается
    # RecipeCreateUpdateSerializer, иначе возвращается RecipeSerializer
    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeCreateUpdateSerializer
        return RecipeSerializer

    # Добавление текущего рецепта в избранное или удаление его из избранного
    @action(
        methods=('post', 'delete'),
        detail=True
    )
    def favorite(self, request, pk):
        return self.perform_action(
            Favorite,
            Recipe,
            RecipeFavoriteSerializer,
            request,
            pk,
            'recipe',
            'Рецепт уже в избранном!',
            'Рецепт отсутствует в избранном!'
        )

    # Добавление текущего рецепта в список покупок или удаление его из списка
    # покупок
    @action(
        methods=('post', 'delete'),
        detail=True
    )
    def shopping_cart(self, request, pk):
        return self.perform_action(
            ShoppingCart,
            Recipe,
            RecipeFavoriteSerializer,
            request,
            pk,
            'recipe',
            'Рецепт уже в корзине!',
            'Рецепт отсутствует в корзине!'
        )

    # Загрузка рецепта в виде txt-файла
    @action(
        methods=('get', ),
        detail=False
    )
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__shoppingcart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(
            amount_sum=Sum('amount')
        ).order_by(
            'ingredient__name'
        )
        shopping_cart = 'Ваш список покупок:\n'
        for ingredient in ingredients:
            shopping_cart += (
                f'{ingredient["ingredient__name"]} - '
                f'{ingredient["amount_sum"]} '
                f'{ingredient["ingredient__measurement_unit"]}\n'
            )
        return HttpResponse(shopping_cart, content_type='text/plain')
