from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrAuthorOrReadOnly(BasePermission):
    """
    Кастомное разрешение: создание и изменение объектов для администраторов и
    авторов. Для остальных пользователей только чтение объекта.
    """

    # Разрешение на выполнение действия на уровне представления (view)
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_authenticated

    # Разрешение на выполнение действия на уровне определенного объекта
    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or obj.author == request.user
