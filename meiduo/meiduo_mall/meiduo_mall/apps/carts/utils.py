import base64
import pickle

from django_redis import get_redis_connection


def merge_cart_cookie_to_redis(request,response,user):
    """
        合并cookie中的购物车数据到redis中
        :param request: 请求对象, 用于获取cookie
        :param response: 响应对象,用于清除cookie
        :param user: 登录用户, 用于获取用户id
        :return:
        """
    # 获取cookie数据
    cookie_cart = request.COOKIES.get('cart')

    if not cookie_cart:
        return response
    dict_cookie_cart = pickle.loads(base64.b64decode(cookie_cart.encode()))
    # 3. 合并cookie数据到redis中, 如果cookie和redis中存在相同的商品,则以cookie中的为准
    redis_conn = get_redis_connection('cart')
    pl = redis_conn.pipeline()
    for sku_id,dict_count_selected in dict_cookie_cart.items():
        count = dict_count_selected['count']
        selected = dict_count_selected['selected']
        pl.hset('cart_%s' % user.id,sku_id,count)
        if selected:
            pl.sadd('cart_selected_%s' % user.id,sku_id)
        else:
            pl.srem('cart_selected_%s' % user.id,sku_id)
    pl.execute()
    # 清楚cookie数据
    response.delete_cookie('cart')
    return response