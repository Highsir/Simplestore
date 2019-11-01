from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

from users.models import User


def jwt_response_payload_handler(token, user=None, request=None):
    """
    自定义jwt认证成功返回数据
    """
    return {
        'token': token,
        'user_id': user.id,
        'username': user.username
    }

class UsernameMobileAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        """判断用户名(手机号)或者密码是否正确"""
        query_set = User.objects.filter(Q(username=username) | Q(mobile=username))
        try:
            if query_set.exists():
                user = query_set.get()  # 取出唯一的一条数据（取不到或者有多条数据都会出错）
                if user.check_password(password):   # 进入一步判断密码是否正确
                    return user
        except:
            return None
