from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """Кастомный пагинатор, для вывода запрошенного количества страниц."""
    page_size_query_param = 'limit'
