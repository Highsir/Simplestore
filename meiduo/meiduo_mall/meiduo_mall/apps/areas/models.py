from django.db import models

from meiduo_mall.utils.models import BaseModel
from users.models import User


class Area(models.Model):
    name = models.CharField(max_length=20,verbose_name='地区名称')
    # 自关联:生成的字段名parent_id
    parent =  models.ForeignKey('self',on_delete=models.SET_NULL,related_name='subs',
                                null=True,blank=True,verbose_name='上级行政区划')
    class Meta:
        db_table = 'tb_areas'
        verbose_name = '行政区划'
        verbose_name_plural = '行政区划'

    def __str__(self):
        return self.name
