from rest_framework import serializers
from PIL import Image as PilImage

from core.mixins import BaseSerializer
from core.models import Partner, Category, Company, Brand, Image, Product, UnitOfMeasure


class CompanySerializer(BaseSerializer):
    class Meta:
        model = Company
        exclude = ["user"]


class PartnerSerializer(BaseSerializer):
    class Meta:
        model = Partner
        fields = "__all__"


class CategorySerializer(BaseSerializer):
    parent_uuid = serializers.UUIDField(write_only=True, required=False)

    class Meta:
        model = Category
        exclude = ["parent"]


class BrandSerializer(BaseSerializer):
    class Meta:
        model = Brand
        fields = "__all__"


class UnitOfMeasureSerializer(BaseSerializer):
    class Meta:
        model = UnitOfMeasure
        fields = "__all__"


### BEGIN - IMAGE ###


class ImageSerializer(BaseSerializer):
    class Meta:
        model = Image
        fields = "__all__"

    def validate_image(self, value):
        valid_image_formats = ["JPEG", "PNG"]
        max_image_size = 2 * 1024 * 1024

        try:
            img = PilImage.open(value)
            if img.format not in valid_image_formats:
                raise serializers.ValidationError(
                    f'Unsupported image format. Allowed formats are: {", ".join(valid_image_formats)}.'
                )
        except Exception as e:
            raise serializers.ValidationError(f"Error processing image: {str(e)}")

        if value.size > max_image_size:
            raise serializers.ValidationError(
                f"Image size exceeds the limit of {max_image_size / (1024 * 1024)}MB."
            )

        return value


### END - IMAGE ###

### BEGIN - PRODUCT ###


class ProductListSerializer(BaseSerializer):
    brand = BrandSerializer(read_only=True)
    unit_of_measure = UnitOfMeasureSerializer(read_only=True)

    class Meta:
        model = Product
        fields = "__all__"


class VariantOptionSerializer(serializers.Serializer):
    name = serializers.CharField()
    values = serializers.ListField(child=serializers.CharField())


class ProductImageSerializer(serializers.Serializer):
    url = serializers.CharField(read_only=True)


class ImageListSerializer(serializers.ListField):
    child = serializers.UUIDField()


class ProductVariantSerializer(serializers.Serializer):
    sku = serializers.CharField()
    name = serializers.CharField()
    cost = serializers.DecimalField(max_digits=10, decimal_places=2)
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    images_data = ImageListSerializer(write_only=True, required=False)


class ProductSerializer(BaseSerializer):
    unit_of_measure_uuid = serializers.UUIDField(write_only=True, required=False)
    brand_uuid = serializers.UUIDField(write_only=True, required=False)
    variant_options_data = VariantOptionSerializer(
        many=True, write_only=True, required=False
    )
    product_variants_data = ProductVariantSerializer(
        many=True, write_only=True, required=False
    )
    images_data = serializers.ListField(
        child=serializers.UUIDField(), write_only=True, required=False
    )

    brand = BrandSerializer(read_only=True)
    unit_of_measure = UnitOfMeasureSerializer(read_only=True)
    product_variants = serializers.SerializerMethodField(read_only=True)
    variant_options = serializers.SerializerMethodField(read_only=True)
    product_images = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Product
        fields = "__all__"

    def get_product_variants(self, instance):
        product_variants = instance.product_variants.all()
        return ProductVariantSerializer(product_variants, many=True).data

    def get_variant_options(self, instance):
        variant_options = instance.variant_options.all()
        data = []
        for variant_option in variant_options:
            option_data = {
                "name": variant_option.name,
                "values": variant_option.variant_values.values_list("value", flat=True),
            }
            data.append(option_data)
        return VariantOptionSerializer(data, many=True).data

    def get_product_images(self, instance):
        product_images = instance.product_images.all()
        data = []
        for product_image in product_images:
            image_data = {"url": product_image.image.url}
            data.append(image_data)
        return ProductImageSerializer(data, many=True).data


### END - PRODUCT ###
