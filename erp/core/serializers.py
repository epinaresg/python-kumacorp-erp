from rest_framework import serializers

from .mixins import (
    BaseListSerializer, BaseModelSerializer
)

from .models import (
    Partner, Category, Company, Brand, UnitOfMeasure,
    Product, ProductVariant, ProductImage,
    VariantOption, VariantValue
)


class CompanySerializer(BaseListSerializer):
    class Meta:
        model = Company
        exclude = ['user']

    def create(self, validated_data):
        user = self.context['request'].user
        try:
            company = Company.objects.get(user=user)
            if company:
                raise serializers.ValidationError("Este usuario ya tiene asignada una compañía.")
        except Company.DoesNotExist:
            pass
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)



class PartnerSerializer(BaseListSerializer, BaseModelSerializer):
    class Meta:
        model = Partner
        fields = '__all__'



class CategorySerializer(BaseListSerializer, BaseModelSerializer):
    parent_uuid = serializers.UUIDField(write_only=True, required=False)

    class Meta:
        model = Category
        exclude = ['parent']

    def create(self, validated_data):
        parent = self.validate_uuid(validated_data.pop('parent_uuid', None), Category)
        if parent and parent.parent:
            raise serializers.ValidationError("Una categoría no puede tener más de un nivel de padres.")
        validated_data['parent'] = parent
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'parent_uuid' in validated_data:
            raise serializers.ValidationError("No se permite actualizar el padre de una categoría.")

        return super().update(instance, validated_data)



class BrandSerializer(BaseListSerializer, BaseModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'



class UnitOfMeasureSerializer(BaseListSerializer, BaseModelSerializer):
    class Meta:
        model = UnitOfMeasure
        fields = '__all__'



class VariantValueSerializer(BaseListSerializer):
    class Meta:
        model = VariantValue
        fields = '__all__'



class VariantOptionSerializer(BaseListSerializer):
    values = VariantValueSerializer(many=True)

    class Meta:
        model = VariantOption
        fields = '__all__'



class ProductSerializer(BaseListSerializer, BaseModelSerializer):
    unit_of_measure_uuid = serializers.UUIDField(write_only=True, required=False)
    brand_uuid = serializers.UUIDField(write_only=True, required=False)
    brand = BrandSerializer(read_only=True)
    unit_of_measure = UnitOfMeasureSerializer(read_only=True)
    variants = VariantOptionSerializer(many=True, write_only=True)

    class Meta:
        model = Product
        fields = '__all__'

    def create(self, validated_data):
        unit_of_measure = self.validate_uuid(validated_data.pop('unit_of_measure_uuid', None), UnitOfMeasure)
        validated_data['unit_of_measure'] = unit_of_measure
        brand = self.validate_uuid(validated_data.pop('brand_uuid', None), Brand)
        validated_data['brand'] = brand
        product = super().create(validated_data)

        variants_data = validated_data.pop('variants', [])
        for variant_data in variants_data:
            values_data = variant_data.pop('values')
            variant_option = VariantOption.objects.create(
                product=product,
                **variant_data)
            for value_data in values_data:
                VariantValue.objects.create(option=variant_option, **value_data)

        return product

class ProductVariantSerializer(BaseListSerializer):
    class Meta:
        model = ProductVariant
        fields = '__all__'

class ProductImageSerializer(BaseListSerializer):
    class Meta:
        model = ProductImage
        fields = '__all__'
