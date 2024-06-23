from rest_framework import serializers
from PIL import Image as PilImage

from core.mixins import BaseSerializer
from core.models import Partner, Category, Company, Brand, Image, Product, ProductVariant, ProductImage, UnitOfMeasure, VariantOption, VariantValue

class CompanySerializer(BaseSerializer):
    class Meta:
        model = Company
        exclude = ['user']

class PartnerSerializer(BaseSerializer):
    class Meta:
        model = Partner
        fields = '__all__'

class CategorySerializer(BaseSerializer):
    parent_uuid = serializers.UUIDField(write_only=True, required=False)

    class Meta:
        model = Category
        exclude = ['parent']

class BrandSerializer(BaseSerializer):
    class Meta:
        model = Brand
        fields = '__all__'

class UnitOfMeasureSerializer(BaseSerializer):
    class Meta:
        model = UnitOfMeasure
        fields = '__all__'

class VariantValueSerializer(BaseSerializer):
    class Meta:
        model = VariantValue
        fields = ['value']

class VariantOptionSerializer(BaseSerializer):
    values = VariantValueSerializer(many=True)

    class Meta:
        model = VariantOption
        fields = ['name', 'values']

class ProductVariantSerializer(BaseSerializer):
    class Meta:
        model = ProductVariant
        fields = ['sku', 'name', 'cost', 'price']

class ProductListSerializer(BaseSerializer):
    brand = BrandSerializer(read_only=True)
    unit_of_measure = UnitOfMeasureSerializer(read_only=True)

    class Meta:
        model = Product
        fields = '__all__'

class ProductSerializer(BaseSerializer):
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

    def get_product_variants(self, instance):
        variants = instance.product_variants.all()
        return ProductVariantSerializer(variants, many=True).data

    def get_variant_options(self, instance):
        options = instance.variant_options.all()
        return VariantOptionSerializer(options, many=True).data

class ProductImageSerializer(BaseSerializer):
    class Meta:
        model = ProductImage
        fields = '__all__'

class ImageSerializer(BaseSerializer):
    class Meta:
        model = Image
        fields = '__all__'

    def validate_image(self, value):
        valid_image_formats = ['JPEG', 'PNG']
        max_image_size = 2 * 1024 * 1024

        try:
            img = PilImage.open(value)
            if img.format not in valid_image_formats:
                raise serializers.ValidationError(f'Unsupported image format. Allowed formats are: {", ".join(valid_image_formats)}.')
        except Exception as e:
            raise serializers.ValidationError(f'Error processing image: {str(e)}')

        if value.size > max_image_size:
            raise serializers.ValidationError(f'Image size exceeds the limit of {max_image_size / (1024 * 1024)}MB.')

        return value
