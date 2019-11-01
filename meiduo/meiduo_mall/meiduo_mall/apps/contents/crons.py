import os
import time
from celery.utils.collections import OrderedDict
from django.template import loader

from contents.models import ContentCategory
from goods.models import GoodsChannel
from meiduo_mall import settings
from meiduo_mall.settings import dev


def generate_static_index_html():
    """生成静态的首页"""
    print('%s: generate_static_index_html' % time.ctime())
    # 1. 获取类别和频道数据
    ordered_dict = get_categories()
    # 2. 获取广告内容（轮播图，快讯，3个楼层数据）
    contents = {}
    content_categories = ContentCategory.objects.all()
    for cate in content_categories:
        # 一查多语法:cate.content_set.all()
        contents[cate.key] = cate.content_set.all().filter(status=True).order_by('sequence')
    # 3. 使用django模板语法渲染模板,得到静态的首页内容
    context = {
        'categories':ordered_dict,
        'contents':contents,
    }
    template = loader.get_template('index.html')
    html_text = template.render(context)
    # 4. 把首页内容写到 front_end_pc/index.html 文件中
    file_path = os.path.join(dev.GENERATED_STATIC_HTML_FILES_DIR,'index.html')
    with open(file_path,'w') as f:
        f.write(html_text)

def get_categories():
    # 拼装满足界面显示需求的数据格式： 商品频道及分类菜单
    ordered_dict = OrderedDict()
    channels = GoodsChannel.objects.order_by('group_id','sequence')
    for channel in channels:
        group_id = channel.group_id # 第n组
        if group_id not in ordered_dict:
            group_dict = {'channels':[],'sub_cats':[]}
            ordered_dict[group_id] = group_dict
        else:
            group_dict = ordered_dict[group_id]
        # 一级类别:{'id':,'name':,'url':}
        cat1 = channel.category
        cat1.url = channel.url
        group_dict['channels'].append(cat1)

        # 二级类别: {'id':, 'name':, 'sub_cats': [{}, {}, {}...]}
        for cat2 in cat1.goodscategory_set.all():
            cat2.sub_cats = [] # 对象新增sub_cats属性
            # 三级类别
            for cat3 in cat2.goodscategory_set.all():
                cat2.sub_cats.append(cat3)
            group_dict['sub_cats'].append(cat2)   # 添加二级类别
    return ordered_dict