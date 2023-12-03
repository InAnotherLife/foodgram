from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Subscription, Tag)
from rest_framework import serializers
from users.models import CustomUser


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов в рецепте."""
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )
    name = serializers.StringRelatedField(source='ingredient.name')
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов (просмотр рецептов)."""
    tags = TagSerializer(many=True)
    author = UserSerializer(default=serializers.CurrentUserDefault())
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    # Получение ингредиентов определенного рецепта
    def get_ingredients(self, obj):
        ingredients = RecipeIngredient.objects.filter(
            recipe=obj
        ).order_by(
            'ingredient__name'
        )
        return RecipeIngredientSerializer(ingredients, many=True).data

    # Получение пользователя и проверка аутентифицирован ли он
    def get_and_check_user(self):
        user = self.context.get('request').user
        if user.is_authenticated:
            return user

    # Получение пользователя и проверка, что рецепт находится в избранном у
    # пользователя
    def get_is_favorited(self, obj):
        user = self.get_and_check_user()
        return user and Favorite.objects.filter(
            user=user,
            recipe=obj
        ).exists()

    # Получение пользователя и проверка, что рецепт находится в списке
    # покупок у пользователя
    def get_is_in_shopping_cart(self, obj):
        user = self.get_and_check_user()
        return user and ShoppingCart.objects.filter(
            user=user,
            recipe=obj
        ).exists()


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов (создание и редактирование рецептов)."""
    author = UserSerializer(default=serializers.CurrentUserDefault())
    ingredients = RecipeIngredientSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    # Получение пользователя и проверка аутентифицирован ли он
    def get_and_check_user(self):
        user = self.context.get('request').user
        if user.is_authenticated:
            return user

    # Получение пользователя и проверка, что рецепт находится в избранном у
    # пользователя
    def get_is_favorited(self, obj):
        user = self.get_and_check_user()
        return user and Favorite.objects.filter(
            user=user,
            recipe=obj
        ).exists()

    # Получение пользователя и проверка, что рецепт находится в списке
    # покупок у пользователя
    def get_is_in_shopping_cart(self, obj):
        user = self.get_and_check_user()
        return user and ShoppingCart.objects.filter(
            user=user,
            recipe=obj
        ).exists()

    # Создание нового рецепта, на основании предоставленных данных
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient_data in ingredients:
            ingredient = ingredient_data.get('ingredient')
            amount = ingredient_data.get('amount')
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=amount
            )
        return recipe

    # Обновление существующего рецепта, на основании предоставленных данных
    def update(self, recipe, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe.tags.clear()
        recipe.ingredients.clear()
        recipe.tags.set(tags)
        for ingredient_data in ingredients:
            ingredient = ingredient_data.get('ingredient')
            amount = ingredient_data.get('amount')
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=amount
            )
        return super().update(recipe, validated_data)

    # Преобразует объект рецепта в словарь для его представления
    def to_representation(self, recipe):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeSerializer(recipe, context=context).data


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для подписки на автора рецепта."""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    # Получение рецептов, созданных автором
    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = Recipe.objects.filter(author=obj)
        recipes_limit = request.query_params.get('recipes_limit')
        context = {'request': request}
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return RecipeFavoriteSerializer(
            recipes,
            many=True,
            context=context).data

    # Получение количества рецептов, созданных автором
    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    # Проверка, что текущий пользователь подписан на автора рецепта
    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return user.is_authenticated and Subscription.objects.filter(
            user=user,
            author=obj
        ).exists()


class RecipeFavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов, находящихся в избранном."""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
