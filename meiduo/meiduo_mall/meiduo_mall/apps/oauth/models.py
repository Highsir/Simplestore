from django.db import models

from meiduo_mall.utils.models import BaseModel


class OauthQQUserModel(BaseModel):
    """
    qq号(openid)与美多用户的关系映射表
    """
    user = models.ForeignKey('users.User',verbose_name='用户')
    openid = models.CharField(max_length=64, verbose_name='openid', db_index=True)

    class Meta:
        db_table = 'tb_oauth_qq'
        verbose_name = 'QQ登录用户数据'
        verbose_name_plural = verbose_name
