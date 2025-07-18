from rest_framework import serializers
from .models import SellerDetailsForm, Category
from form.models import Form


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class SellerDetailsFormSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)

    category_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    # ✅ Accept UUID in POST/PUT
    user_uuid = serializers.UUIDField(write_only=True)

    # ✅ Output UUID in GET
    user_uuid_display = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = SellerDetailsForm
        fields = [
            'id',
            'user_uuid',           # write-only
            'user_uuid_display',   # read-only
            'store_name',
            'categories',
            'category_ids',
            'inventory_estimate',
            'specialization',
            'created_at',
        ]
        extra_kwargs = {
            'user_uuid': {'write_only': True},
        }

    def get_user_uuid_display(self, obj):
        return str(obj.user.uuid) if obj.user else None

    def validate_user_uuid(self, value):
        try:
            user = Form.objects.get(uuid=value)
            return user
        except Form.DoesNotExist:
            raise serializers.ValidationError("User with this UUID does not exist.")

    def validate_inventory_estimate(self, value):
        allowed_choices = dict(SellerDetailsForm.INVENTORY_CHOICES).keys()
        if value not in allowed_choices:
            raise serializers.ValidationError(f"'{value}' is not a valid choice.")
        return value

    def create(self, validated_data):
        category_ids = validated_data.pop('category_ids', [])
        user = validated_data.pop('user_uuid')
        validated_data['user'] = user

        seller = SellerDetailsForm.objects.create(**validated_data)
        if category_ids:
            seller.categories.set(Category.objects.filter(id__in=category_ids))
        return seller

    def update(self, instance, validated_data):
        category_ids = validated_data.pop('category_ids', None)
        user = validated_data.pop('user_uuid', None)
        if user:
            instance.user = user

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if category_ids is not None:
            instance.categories.set(Category.objects.filter(id__in=category_ids))

        return instance
