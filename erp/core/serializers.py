from rest_framework import serializers
from django.db import transaction

from .mixins import (
    BaseListSerializer, BaseModelSerializer
)

from .models import (
    Partner, Category, Company, Brand, UnitOfMeasure,
    Product, ProductVariant, ProductImage,
    VariantOption, VariantValue
)

from .services import (
    ProductVariantService
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
        fields = ['value']


class VariantOptionSerializer(BaseListSerializer):
    values = VariantValueSerializer(many=True)

    class Meta:
        model = VariantOption
        fields = ['name', 'values']


class ProductVariantSerializer(BaseListSerializer):
    class Meta:
        model = ProductVariant
        fields = ['sku', 'name', 'cost', 'price']

class ProductListSerializer(BaseListSerializer):
    brand = BrandSerializer(read_only=True)
    unit_of_measure = UnitOfMeasureSerializer(read_only=True)
    class Meta:
        model = Product
        fields = '__all__'

class ProductSerializer(BaseModelSerializer):
    unit_of_measure_uuid = serializers.UUIDField(write_only=True, required=False)
    brand_uuid = serializers.UUIDField(write_only=True, required=False)
    variant_options_data = VariantOptionSerializer(many=True, write_only=True, required=False)
    product_variants_data = ProductVariantSerializer(many=True, write_only=True, required=False)

    brand = BrandSerializer(read_only=True)
    unit_of_measure = UnitOfMeasureSerializer(read_only=True)
    product_variants = serializers.SerializerMethodField(read_only=True)
    variant_options = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Product
        fields = '__all__'

    def set_custom_data(self, validated_data):
        unit_of_measure_uuid = validated_data.pop('unit_of_measure_uuid', None)
        brand_uuid = validated_data.pop('brand_uuid', None)

        unit_of_measure = self.validate_uuid(unit_of_measure_uuid, UnitOfMeasure)
        brand = self.validate_uuid(brand_uuid, Brand)

        validated_data['unit_of_measure'] = unit_of_measure
        validated_data['brand'] = brand
        return validated_data

    def create(self, validated_data):
        print('CREATE 1')
        validated_data = self.set_custom_data(validated_data)
        print('CREATE 2')
        with transaction.atomic():
            variant_options_data = validated_data.pop('variant_options_data', [])
            product_variants_data = validated_data.pop('product_variants_data', [])

            product = super().create(validated_data)

            service = ProductVariantService()
            product = service.create(product, variant_options_data)
            service.set_product_variants_data(product, product_variants_data)
        return product

    def update(self, instance, validated_data):
        validated_data = self.set_custom_data(validated_data)
        with transaction.atomic():
            variant_options_data = validated_data.pop('variant_options_data', [])
            product_variants_data = validated_data.pop('product_variants_data', [])
            product = super().update(instance, validated_data)
            service = ProductVariantService()
            service.create(product, variant_options_data)
            service.set_product_variants_data(product, product_variants_data)
        return product

    def get_product_variants(self, instance):
        variants = ProductVariant.objects.filter(product=instance)
        serializer = ProductVariantSerializer(variants, many=True)
        return serializer.data

    def get_variant_options(self, instance):
        options = VariantOption.objects.filter(product=instance)
        serializer = VariantOptionSerializer(options, many=True)
        return serializer.data

class ProductImageSerializer(BaseListSerializer):
    class Meta:
        model = ProductImage
        fields = '__all__'
