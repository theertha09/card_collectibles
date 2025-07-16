from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import Form,Address

class FormSerializer(serializers.ModelSerializer):
    reenter_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Form
        fields = ['uuid', 'full_name','last_name' ,'email', 'phone_number', 'gender', 'password', 'reenter_password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, data):
        if data['password'] != data['reenter_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        validated_data.pop('reenter_password')
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)


 

class UserInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Form
        fields = ['full_name', 'last_name', 'email', 'phone_number']


class AddressSerializer(serializers.ModelSerializer):
    user = UserInfoSerializer(read_only=True)
    user_uuid = serializers.UUIDField(write_only=True, required=True)

    class Meta:
        model = Address
        fields = [
            'id',
            'user',
            'user_uuid',
            'house_name',
            'street_name',
            'country',
            'state',
            'pin',
            'city',
            'image',
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
