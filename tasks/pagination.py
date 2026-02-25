from rest_framework.pagination import PageNumberPagination, CursorPagination
from rest_framework.response import Response


class TaskCursorPagination(CursorPagination):
    """
    Cursor based pagination - does NOT run COUNT(*) on the full table.
    This is the key performance fix for large datasets.

    PageNumberPagination runs: SELECT COUNT(*) FROM tasks WHERE user_id=x <- slow on large datasets
    PageNumberPagination runs: SELECT ... WHERE id < <cursor> LIMIT 20 <- always fast

    Trade off: no page numbers, only next/previous links (perfect for infinite scroll).
    """
    page_size = 20
    ordering = '-created_at' # must match an indexed field
    cursor_query_param = 'cursor'

    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
        })

    def get_paginated_response_schema(self, schema):
        return{
            'type': 'object',
            'properties': {
                'next': {'type': 'string', 'nullable': True},
                'previous': {'type': 'string', 'nullable': True},
                'results': schema,
            }
        }

class TaskPageNumberPagination(PageNumberPagination):
    """
    Optional: classic page-number pagination with fast COUNT workaround.
    Use this only if you need ?page=N style navigation.
    Avoid on large datasets - use TaskCursorPagination instead.
    """

    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
            'page': self.page.number,
            'pages': self.page.paginator.num_pages,
        })
