from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import Form, Address

class FormSerializer(serializers.ModelSerializer):
    reenter_password = serializers.CharField(write_only=True, required=True)
    referral_code = serializers.CharField(read_only=True)
    referred_by_code = serializers.CharField(write_only=True, required=False, allow_blank=True)
    unique_link = serializers.SerializerMethodField()
    referral_link = serializers.SerializerMethodField()
    qr_code_url = serializers.SerializerMethodField()

    class Meta:
        model = Form
        fields = [
            'uuid', 'full_name', 'last_name', 'email', 'phone_number',
            'gender', 'password', 'reenter_password', 'referral_code', 'referred_by_code',
            'unique_link', 'referral_link', 'qr_code_url',
            'unique_link_token', 'link_click_count', 'is_link_active',
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'unique_link_token': {'read_only': True},
            'link_click_count': {'read_only': True},
        }

    def get_unique_link(self, obj):
        return obj.get_unique_link()

    def get_referral_link(self, obj):
        return obj.get_referral_link()

    def get_qr_code_url(self, obj):
        if obj.qr_code_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.qr_code_image.url)
            return obj.qr_code_image.url
        return None

    def validate(self, data):
        if self.instance is None:
            # On create, check password match
            if not data.get('password') or not data.get('reenter_password'):
                raise serializers.ValidationError("Both password and reenter_password are required.")
            if data.get('password') != data.get('reenter_password'):
                raise serializers.ValidationError("Passwords do not match.")
        elif 'password' in data or 'reenter_password' in data:
            # On update, if password is being updated, validate match
            if data.get('password') != data.get('reenter_password'):
                raise serializers.ValidationError("Passwords do not match.")
            
        return data
    def create(self, validated_data):
        referred_by_code = validated_data.pop('referred_by_code', None)
        validated_data.pop('reenter_password')
        validated_data['password'] = make_password(validated_data['password'])

        user = Form(**validated_data)

        if referred_by_code:
            try:
                referrer = Form.objects.get(referral_code=referred_by_code)
                user.referred_by = referrer
            except Form.DoesNotExist:
                raise serializers.ValidationError({'referred_by_code': 'Invalid referral code.'})

        user.save()
        return user


class UserInfoSerializer(serializers.ModelSerializer):
    referral_code = serializers.CharField(read_only=True)
    unique_link = serializers.SerializerMethodField()
    referral_link = serializers.SerializerMethodField()

    class Meta:
        model = Form
        fields = ['full_name', 'last_name', 'email', 'phone_number', 'referral_code', 'unique_link', 'referral_link']

    def get_unique_link(self, obj):
        return obj.get_unique_link()

    def get_referral_link(self, obj):
        return obj.get_referral_link()


class AddressSerializer(serializers.ModelSerializer):
    user = UserInfoSerializer(read_only=True)
    user_uuid = serializers.UUIDField(write_only=True, required=True)

    class Meta:
        model = Address
        fields = [
            'id', 'user', 'user_uuid', 'house_name', 'street_name',
            'country', 'state', 'pin', 'city', 'image',
        ]

    def create(self, validated_data):
        user_uuid = validated_data.pop('user_uuid')
        try:
            user = Form.objects.get(uuid=user_uuid)
        except Form.DoesNotExist:
            raise serializers.ValidationError({'user_uuid': 'User not found.'})
        validated_data['user'] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        user_uuid = validated_data.pop('user_uuid', None)
        if user_uuid:
            try:
                user = Form.objects.get(uuid=user_uuid)
                instance.user = user
            except Form.DoesNotExist:
                raise serializers.ValidationError({'user_uuid': 'User not found.'})
        return super().update(instance, validated_data)
