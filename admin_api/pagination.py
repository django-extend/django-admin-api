from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class PagePagination(PageNumberPagination):
    page = None
    request = None
    page_size = 100
    page_size_query_param = 'pageSize'
    page_query_param = 'pageNo'

    def get_paginated_response(self, data):
        result = {
            'data': data,
            'pageSize': self.page_size,
            'pageNo': self.page.number,
            'totalPage': self.page.paginator.num_pages,
            'totalCount': self.page.paginator.count,
        }
        response = {
            'message': '',
            'status': 200,
            'result': result,
        }
        return Response(response)

    def paginate_queryset(self, queryset, request, view=None):
        if request.query_params.get(self.page_size_query_param) == '-1':
            self.page_size = 9999999 # 设置一个极限值，逻辑比较简单
        self.page_size = self.get_page_size(request)
        page_number = request.query_params.get(self.page_query_param, 1)
        paginator = self.django_paginator_class(queryset, self.page_size)
        self.page = paginator.page(page_number)
        self.request = request
        return list(self.page)
