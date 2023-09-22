from django.conf import settings
from rest_framework.pagination import PageNumberPagination


class LimitPageNumberPagination(PageNumberPagination):
    """ Пагинация. """
    page_size = settings.DEFAULT_PAGE_SIZE
    page_size_query_param = 'limit'
