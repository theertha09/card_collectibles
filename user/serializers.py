from rest_framework import serializers
from .models import UserForm, SellerDetailsForm, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class SellerDetailsFormSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)

    category_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True
    )

    # ✅ Show UUID in GET response (read-only)
    user_uuid = serializers.SerializerMethodField()

    # ✅ Accept UUID in POST/PUT (write-only)
    user_uuid_input = serializers.UUIDField(write_only=True, required=False)

    class Meta:
        model = SellerDetailsForm
        fields = [
            'id',
            'user',
            'user_uuid',         # ✅ shown in GET
            'user_uuid_input',   # ✅ accepted in POST
            'store_name',
            'categories',
            'category_ids',
            'inventory_estimate',
            'specialization',
            'created_at',
        ]
        extra_kwargs = {
            'user': {'write_only': True},
        }

    def get_user_uuid(self, obj):
        return str(obj.user.uuid) if obj.user and obj.user.uuid else None

    def to_internal_value(self, data):
        data = data.copy() if hasattr(data, 'copy') else dict(data)

        # Convert UUID to user ID
        if 'user_uuid_input' in data:
            try:
                user = UserForm.objects.get(uuid=data['user_uuid_input'])
                data['user'] = user.id
                del data['user_uuid_input']
            except UserForm.DoesNotExist:
                raise serializers.ValidationError({'user_uuid_input': 'User not found'})
            except ValueError:
                raise serializers.ValidationError({'user_uuid_input': 'Invalid UUID format'})

        return super().to_internal_value(data)

    def create(self, validated_data):
        category_ids = validated_data.pop('category_ids', [])
        seller_details = SellerDetailsForm.objects.create(**validated_data)
        if category_ids:
            seller_details.categories.set(Category.objects.filter(id__in=category_ids))
        return seller_details

    def update(self, instance, validated_data):
        category_ids = validated_data.pop('category_ids', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if category_ids is not None:
            instance.categories.set(Category.objects.filter(id__in=category_ids))

        return instance


class UserFormSerializer(serializers.ModelSerializer):
    seller_details = SellerDetailsFormSerializer(many=True, read_only=True)

    class Meta:
        model = UserForm
        fields = '__all__'
