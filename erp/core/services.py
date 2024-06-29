from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import get_object_or_404
from itertools import product as itertools_product
from rest_framework.exceptions import ValidationError

from core.models import (
    Brand,
    Category,
    Company,
    Image,
    Product,
    ProductImage,
    ProductVariant,
    VariantOption,
    VariantValue,
    UnitOfMeasure,
)


class UtilService:
    def validate_uuid(*, uuid: str, model_class):
        if uuid:
            instance = get_object_or_404(model_class=model_class, uuid=uuid)
            return instance
        return None

    def validate_if_name_is_used(*, action, validated_data, model_class, instance=None):
        if (
            model_class == Category
            and "parent" in validated_data
            and isinstance(validated_data["parent"], Category)
        ):
            name = validated_data["name"]
            parent = validated_data["parent"]
            queryset = model_class.objects.filter(
                name=name, company=validated_data["company"], parent=parent
            )
            error_message = (
                f"A subcategory with the name '{name}' already exists for this parent."
            )
        else:
            name = validated_data["name"]
            queryset = model_class.objects.filter(
                name=name, company=validated_data["company"]
            )
            error_message = f"A {model_class.__name__.lower()} with the name '{name}' already exists."

        if action == "update" and instance:
            queryset = queryset.exclude(pk=instance.pk)

        if queryset.exists():
            raise ValidationError(error_message)


class CompanyService:
    def create(*, user: User, serializer):
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        if Company.objects.filter(user=user).exists():
            raise serializer.ValidationError(
                "Este usuario ya tiene asignada una compañía."
            )

        validated_data["user"] = user

        return serializer.save()

    def update(*, serializer):
        serializer.is_valid(raise_exception=True)
        return serializer.save()


class CategoryService:
    def create(*, company: Company, serializer):
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        parent_uuid = validated_data.pop("parent_uuid", None)
        parent = UtilService.validate_uuid(uuid=parent_uuid, model_class=Category)
        if parent and parent.parent:
            raise serializer.ValidationError(
                "Una categoría no puede tener más de un nivel de padres."
            )

        validated_data.update({"company": company, "parent": parent})
        UtilService.validate_if_name_is_used(
            action="create", validated_data=validated_data, model_class=Category
        )
        return serializer.save()

    def update(*, serializer):
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        instance = serializer.instance
        validated_data["company"] = instance.company

        UtilService.validate_if_name_is_used(
            action="update",
            validated_data=validated_data,
            model_class=Category,
            instance=serializer.instance,
        )
        return serializer.save()


class ProductService:
    def set_custom_data(self, *, validated_data):
        unit_of_measure_uuid = validated_data.pop("unit_of_measure_uuid", None)
        brand_uuid = validated_data.pop("brand_uuid", None)

        validated_data["unit_of_measure"] = UtilService.validate_uuid(
            uuid=unit_of_measure_uuid, model_class=UnitOfMeasure
        )
        validated_data["brand"] = UtilService.validate_uuid(
            uuid=brand_uuid, model_class=Brand
        )

        return validated_data

    def create(self, *, company: Company, serializer):
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        validated_data["company"] = company

        UtilService.validate_if_name_is_used(
            action="create", validated_data=validated_data, model_class=Product
        )
        validated_data = self.set_custom_data(validated_data=validated_data)

        variant_options_data = validated_data.pop("variant_options_data", [])
        product_variants_data = validated_data.pop("product_variants_data", [])
        images_data = validated_data.pop("images_data", [])
        with transaction.atomic():
            product = serializer.save()

            product_variant_service = ProductVariantService()
            product_variant_service.create(
                product=product, variant_options_data=variant_options_data
            )
            product_variant_service.set_product_variants_data(
                product=product, product_variants_data=product_variants_data
            )

            ProductImageService.create(product=product, images_data=images_data)

            product.has_variants = bool(variant_options_data)
            product.save(update_fields=["has_variants"])

        return product

    def update(self, *, serializer):
        serializer.is_valid(raise_exception=True)

        product = serializer.instance

        validated_data = serializer.validated_data
        validated_data["company"] = product.company

        UtilService.validate_if_name_is_used(
            action="update",
            validated_data=validated_data,
            model_class=Product,
            instance=product,
        )
        validated_data = self.set_custom_data(validated_data=validated_data)

        variant_options_data = validated_data.pop("variant_options_data", [])
        product_variants_data = validated_data.pop("product_variants_data", [])
        images_data = validated_data.pop("images_data", [])
        with transaction.atomic():
            product.save()

            product_variant_service = ProductVariantService()
            product_variant_service.create(
                product=product, variant_options_data=variant_options_data
            )
            product_variant_service.set_product_variants_data(
                product=product, product_variants_data=product_variants_data
            )

            ProductImageService.create(product=product, images_data=images_data)

            product.has_variants = bool(variant_options_data)
            product.save(update_fields=["has_variants"])

        return product


class ProductImageService:
    @transaction.atomic
    def create(*, product, images_data):
        image_ids = []
        for image_uuid in images_data:
            image = UtilService.validate_uuid(uuid=image_uuid, model_class=Image)
            product_image = ProductImage.objects.create(
                company=product.company, product=product, image=image
            )
            image_ids.append(product_image.id)

            image.in_use = True
            image.save()

        ProductImage.objects.filter(company=product.company, product=product).exclude(
            id__in=image_ids
        ).delete()


class ProductVariantService:
    @transaction.atomic
    def create(self, *, product, variant_options_data):
        self.create_variants(product=product, variant_options_data=variant_options_data)
        self.generate_product_variants(product=product)

    @transaction.atomic
    def set_product_variants_data(self, *, product, product_variants_data):
        for product_variant_data in product_variants_data:
            product_variant = get_object_or_404(
                model_class=ProductVariant,
                company=product.company,
                product=product,
                name=product_variant_data["name"],
            )
            product_variant.sku = product_variant_data["sku"]
            product_variant.cost = product_variant_data["cost"]
            product_variant.price = product_variant_data["price"]
            product_variant.save()

    def generate_product_variants(self, *, product):
        variant_options = VariantOption.objects.filter(
            company=product.company, product=product
        )

        option_values = []
        for option in variant_options:
            values = VariantValue.objects.filter(company=product.company, option=option)
            option_values.append(values)

        combinations = list(itertools_product(*option_values))
        option_names = " ".join([option.name for option in variant_options])
        product_variant_ids = []
        for combination in combinations:
            if combination:
                variant_name = (
                    option_names
                    + " - "
                    + (" ".join([value.value for value in combination]))
                )
                product_variant, created = ProductVariant.objects.get_or_create(
                    company=product.company,
                    product=product,
                    name=variant_name,
                    defaults={"cost": 0, "price": 0, "stock_quantity": 0},
                )
                product_variant_ids.append(product_variant.id)

        ProductVariant.objects.filter(company=product.company, product=product).exclude(
            id__in=product_variant_ids
        ).delete()

        return len(product_variant_ids)

    def create_variants(self, *, product, variant_options_data):
        variant_option_ids = []
        for variant_option_data in variant_options_data:
            variant_option, created = VariantOption.objects.get_or_create(
                company=product.company,
                product=product,
                name=variant_option_data["name"],
            )
            variant_option_ids.append(variant_option.id)
            variant_values_data = variant_option_data.pop("values")
            for value in variant_values_data:
                VariantValue.objects.get_or_create(
                    company=product.company,
                    product=product,
                    option=variant_option,
                    value=value,
                )

        VariantOption.objects.filter(company=product.company, product=product).exclude(
            id__in=variant_option_ids
        ).delete()
