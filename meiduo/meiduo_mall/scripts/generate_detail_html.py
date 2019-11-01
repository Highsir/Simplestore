# 1. 添加导包路径 (把 scripts 的上一级目录添加到导包路径sys.path)
import sys
sys.path.insert(0, '../')

# 2. 设置配置文件，初始化django环境
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_mall.settings.dev")
django.setup()

# 3. 导包
from celery_tasks.html.tasks import generate_static_sku_detail_html
from goods.models import SKU

# 4. 功能逻辑
if __name__ == '__main__':
    skus = SKU.objects.all()
    for sku in skus:
        print(sku.id)
        generate_static_sku_detail_html(sku.id)
