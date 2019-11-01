import re

from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer
from rest_framework_jwt.settings import api_settings

from celery_tasks import email
from celery_tasks.email.tasks import send_verify_email
from goods.models import SKU
from users.models import User, Address


class CreateUserSerializer(ModelSerializer):
    password2 = serializers.CharField(label='确认密码', write_only=True)
    sms_code = serializers.CharField(label='短信验证码', write_only=True)
    allow = serializers.BooleanField(label='同意协议', write_only=True)
    token = serializers.CharField(label='登录状态token', read_only=True)

    def create(self, validated_data):

        print(self.context.get('format'))
        print(self.context.get('request').user)
        print(self.context.get('view'))
        # User.objects.create()             # 不会对密码进行加密
        user = User.objects.create_user(  # 会对密码进行加密
            username=validated_data.get('username'),
            password=validated_data.get('password'),
            mobile=validated_data.get('mobile'))
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        user.token = token
        return user

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'password2',
                  'sms_code', 'mobile', 'allow','token')

        extra_kwargs = {
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许5-20个字符的用户名',
                    'max_length': '仅允许5-20个字符的用户名',
                }
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            }
        }

    def validate_mobile(self, value):
        """验证手机号"""
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式错误')
        return value

    def validate_allow(self, value):
        """检验用户是否同意协议"""
        if not value:
            raise serializers.ValidationError('请同意用户协议')
        return value

    def validate(self, attrs):
        # 判断两次密码
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError('两次密码不一致')

        # 判断短信验证码
        redis_conn = get_redis_connection('sms_codes')
        mobile = attrs['mobile']
        real_sms_code = redis_conn.get('sms_%s' % mobile)
        if not real_sms_code:
            raise ValidationError('无效的短信验证码')
        if attrs.get('sms_code') != real_sms_code.decode():
            raise ValidationError('短信验证码错误')

        return attrs

class UserDetailSerializer(serializers.ModelSerializer):
    """用户详情信息序列化器"""
    class Meta:
        model = User
        fields = ('id', 'username','mobile','email','email_active')

class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','email')
        extra_kwargs = {
            'email':{
                'required':True
            }
        }
    def update(self, instance, validated_data):
        instance.email = validated_data['email']
        instance.save()
        # 发送邮件
        verify_url = instance.generate_verify_email_url()
        send_verify_email.delay(instance.email,verify_url)
        return instance

class UserAddressSerializer(serializers.ModelSerializer):
    province = serializers.StringRelatedField(read_only=True)
    city = serializers.StringRelatedField(read_only=True)
    district = serializers.StringRelatedField(read_only=True)

    province_id = serializers.IntegerField(label='省ID',required=True)
    city_id = serializers.IntegerField(label='市ID',required=True)
    district_id = serializers.IntegerField(label='区ID',required=True)

    def validata_mobile(self,value):
        if not re.match(r'1[3-9]\d{9}$',value):
            raise serializers.ValidationError('手机号格式错误')
        return value

    def create(self, validated_data):
        """保存"""
        validated_data['user'] = self.context['request'].user
        return super(UserAddressSerializer,self).create(validated_data)

    class Meta:
        model = Address
        exclude = ('user','is_deleted','create_time','update_time')

class AddBrowseHistorySerializer(serializers.Serializer):
    """
    添加用户浏览历史序列化器
    """
    sku_id = serializers.IntegerField(label='商品SKU编号',min_value=1)

    def validate_sku_id(self,value):
        """
        检验sku_id是否存在
        """
        try:
            SKU.objects.get(id=value)
        except SKU.DoesNotExist:
            raise serializers.ValidationError('该商品不存在')

    def create(self, validated_data):
        """
        保存
        """
        user_id = self.user.id      # 在视图中使用序列化器时,视图给序列化器新增的字段
        sku_id = validated_data['sku_id']

        redis_conn = get_redis_connection('history')
        pl = redis_conn.pipeline()

        # 移除已经存在的本商品浏览记录
        pl.lrem("history_%s" % user_id,0,sku_id)
        # 添加新的浏览记录
        pl.lpush('history_%s' % user_id,sku_id)
        # 最多只保存5条记录
        pl.ltrim('history_%s' % user_id,0,4)
        pl.execute()
        return validated_data






























