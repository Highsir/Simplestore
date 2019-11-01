from haystack import indexes

from goods.models import SKU


class SKUIndex(indexes.SearchIndex,indexes.Indexable):
    """
    SKU索引类
    """
    text = indexes.CharField(document=True,use_template=True)
    # 保存在索引库中的字段
    id = indexes.IntegerField(model_attr='id')
    name = indexes.CharField(model_attr='name')
    price = indexes.DecimalField(model_attr='price')
    default_image_url = indexes.CharField(model_attr='default_image_url')
    comments = indexes.IntegerField(model_attr='comments')

    def get_model(self):
        """返回建立索引的模型类"""
        return SKU

    def index_queryset(self, using=None):
        """返回要建立索引的数据查询集"""
        return self.get_model().objects.filter(is_launched = True)