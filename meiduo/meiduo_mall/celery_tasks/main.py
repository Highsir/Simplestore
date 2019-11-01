import os

from celery import Celery
# 1. 设置配置文件, 需要放置到创建celery对象之前
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_mall.settings.dev")
# 创建了一个celery应用
# 参数1: 自定义的一个名字
# 参数2：异步任务保存到 redis 中
celery_app = Celery('meiduo',
                    broker='redis://127.0.0.1:6379/15',
                    backend='redis://127.0.0.1:6379/14',
                    )
# 指定对应的包,扫描celery任务
celery_app.autodiscover_tasks(['generate_static_sku_detail_html',
                               'celery_tasks.html',
                                'celery_tasks.sms',
                               'celery_tasks.email'])