from django_redis import get_redis_connection
from rest_framework import serializers

from oauth.models import OauthQQUserModel
from oauth.utils import check_encrypted_openid
from users.models import User


class QQUserSerializer(serializers.Serializer):
    openid = serializers.CharField(label='openid',write_only=True)
    mobile = serializers.RegexField(label='手机号', regex=r'^1[3-9]\d{9}$',
                                    write_only=True)
    password = serializers.CharField(label='密码', max_length=20, min_length=8,write_only = True)
    sms_code = serializers.CharField(label='短信验证码', write_only=True)

    def validate(self, attrs):
        # 获取openid, 校验openid是否有效
        encrypted_openid = attrs['openid']  # 加密后的openid
        openid = check_encrypted_openid(encrypted_openid)
        if not openid:
            raise serializers.ValidationError('无效的openid')
        # 修改字典中opendi的值， 以便保存正确的openid到映射表
        attrs['openid'] = openid
        mobile = attrs['mobile']
        sms_code = attrs['sms_code']
        password = attrs['password']
        # 校验短信验证码
        redis_conn = get_redis_connection('sms_codes')
        real_sms_code = redis_conn.get('sms_%s' % mobile)
        if not real_sms_code:
            raise serializers.ValidationError('短信验正码无效')
        if real_sms_code.decode() != sms_code:
            raise serializers.ValidationError('短信验证码错误')

        try:
            user = User.objects.get(mobile=mobile)
            if not user.check_password(password):
                raise serializers.ValidationError('密码错误')
        except User.DoesNotExist:

            user = User.objects.create_user(
                username=mobile,
                password=password,
                mobile=mobile,
            )
        attrs['user'] = user
        return attrs

    def create(self, validated_data):
        # 获取校验的用户
        user = validated_data.get('user')
        openid = validated_data.get('openid')

        # 绑定openid和美多用户： 新增一条表数据
        OauthQQUserModel.objects.create(
            openid=openid,
            user=user
        )
        return user  # 返回美多用户对象
