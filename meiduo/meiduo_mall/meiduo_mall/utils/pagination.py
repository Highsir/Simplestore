from rest_framework.pagination import PageNumberPagination


class MyPageNumberPagination(PageNumberPagination):
    page_size = 2  # 默认每页显示2条
    page_query_param = 'page'  # 查询关键字名称：第几页
    page_size_query_param = 'page_size'  # 查询关键字名称：每页多少条