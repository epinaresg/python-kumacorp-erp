from itertools import product as itertools_product
from django.db import transaction

from .models import (
    ProductVariant, VariantOption, VariantValue
)

class ProductVariantService:

    @transaction.atomic
    def create(self, product, variant_options_data):
        self.create_variants(product, variant_options_data)
        product_varians_qty = self.generate_product_variants(product)

        product.has_variants = False
        if product_varians_qty > 0:
            print('HAS VARIANTS')
            product.has_variants = True
        product.save()

        return product

    @transaction.atomic
    def set_product_variants_data(self, product, product_variants_data):
        print('SET PRODUCT VARIANTS DATA', product_variants_data)
        for product_variant_data in product_variants_data:
            product_variant = ProductVariant.objects.get(
                company=product.company,
                product=product,
                name=product_variant_data['name']
            )
            print('PRODUCT VARIANT', product_variant)
            product_variant.sku = product_variant_data['sku']
            product_variant.cost = product_variant_data['cost']
            product_variant.price = product_variant_data['price']

            product_variant.save()

    def generate_product_variants(self, product):
        print('GENERATE PRODUCT VARIANTS')
        variant_options = VariantOption.objects.filter(
            company=product.company,
            product=product
        )

        option_values = []
        for option in variant_options:
            values = VariantValue.objects.filter(
                company=product.company,
                option=option
            )
            option_values.append(values)

        combinations = list(itertools_product(*option_values))
        option_names = ' ' . join([option.name for option in variant_options])
        product_variant_ids = []
        print("COMBINATIONS", combinations)
        for combination in combinations:
            if combination:
                print("COMBINATION", combination)
                variant_name = option_names + ' - ' + (' ' . join([value.value for value in combination]))
                product_variant, created = ProductVariant.objects.get_or_create(
                    company=product.company,
                    product=product,
                    name=variant_name,
                    defaults={
                        'cost': 0,
                        'price': 0,
                        'stock_quantity': 0
                    }
                )
                product_variant_ids.append(product_variant.id)

        print("PRODUCT VARIANTS ID", product_variant_ids)
        ProductVariant.objects.filter(
            company=product.company,
            product=product
        ).exclude(id__in=product_variant_ids).delete()

        return len(product_variant_ids)


    def create_variants(self, product, variant_options_data):
        variant_option_ids = []
        for variant_option_data in variant_options_data:
            variant_option, created = VariantOption.objects.get_or_create(
                company=product.company,
                product=product,
                name=variant_option_data['name']
            )
            variant_option_ids.append(variant_option.id)
            variant_values_data = variant_option_data.pop('values')
            for variant_value_data in variant_values_data:
                VariantValue.objects.get_or_create(
                    company=product.company,
                    product=product,
                    option=variant_option,
                    value=variant_value_data['value']
                )

        print("CREATE VARIANTS", variant_option_ids)
        VariantOption.objects.filter(
            company=product.company,
            product=product
        ).exclude(id__in=variant_option_ids).delete()

