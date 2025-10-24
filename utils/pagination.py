from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10  # default page size
    page_size_query_param = "limit"  # allow ?limit=50
    max_page_size = 100  # prevent abuse

    def get_paginated_data(self, data):
        return {
            "count": self.page.paginator.count,
            "page": self.page.number,
            "limit": self.get_page_size(self.request),
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "results": data,
        }
