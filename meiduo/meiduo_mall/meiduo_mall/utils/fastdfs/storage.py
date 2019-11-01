from django.core.files.storage import FileSystemStorage
from fdfs_client.client import Fdfs_client

from meiduo_mall import settings


class FastDFSStorage(FileSystemStorage):
    """自定义文件存储系统类"""
    def _save(self, name, content):
        """
        当用户通过django管理后台上传文件时, 调用此方法保存文件到FastDFS服务器中
        :param
        name: 传入的文件名
        :param
        content: 文件内容
        :return: 上传文件的路径
        """
        # todo: 自定义存储：保存文件到FastDFS服务器
        client = Fdfs_client('meiduo_mall/utils/fastdfs/client.conf')
        dict_data = client.upload_by_buffer(content.read())
        if 'Upload successed.' != dict_data.get('Status'):
            raise Exception('上传文件到FastDFS失败')
        # 获取文件id
        path = dict_data.get('Remote file_id')
        return path
    def url(self, name):
        """
                返回文件的完整URL路径
                :param name: 数据库中保存的文件名，类似：
                             group1/M00/00/00/wKjSoFu-wD2AZQ6ZAAERuQ5dzms593.png
                :return: 完整的URL
                """
        return settings.FDFS_URL + name