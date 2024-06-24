from django.db import models
from django_extensions.db.models import TimeStampedModel
from django_softdelete.models import SoftDeleteModel
from django.conf import settings
import uuid

class Company(TimeStampedModel, SoftDeleteModel):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, verbose_name="UUID")
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="User")
    name = models.CharField(max_length=255, verbose_name="Name")
    settings = models.JSONField(default=dict, verbose_name="Settings")

    def __str__(self):
        return self.name

class Partner(TimeStampedModel, SoftDeleteModel):
    company = models.ForeignKey(Company, on_delete=models.DO_NOTHING, verbose_name="Company", related_name='partners')
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True, verbose_name="UUID")
    is_customer = models.BooleanField(default=False, verbose_name="Is Customer")
    is_supplier = models.BooleanField(default=False, verbose_name="Is Supplier")
    name = models.CharField(max_length=255, verbose_name="Name")
    tax_id = models.CharField(max_length=50, null=True, blank=True, verbose_name="Tax ID")
    address = models.TextField(null=True, blank=True, verbose_name="Address")
    email = models.EmailField(null=True, blank=True, verbose_name="Email")
    phone_number = models.CharField(max_length=50, null=True, blank=True, verbose_name="Phone Number")

    def __str__(self):
        return self.name

class Category(TimeStampedModel, SoftDeleteModel):
    company = models.ForeignKey(Company, on_delete=models.DO_NOTHING, verbose_name="Company", related_name='categories')
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True, verbose_name="UUID")
    name = models.CharField(max_length=255, verbose_name="Name")
    description = models.TextField(null=True, blank=True, verbose_name="Description")
    parent = models.ForeignKey('self', related_name='children', on_delete=models.CASCADE, null=True, blank=True, verbose_name="Parent Category")

    def __str__(self):
        return self.name

class Brand(TimeStampedModel, SoftDeleteModel):
    company = models.ForeignKey(Company, on_delete=models.DO_NOTHING, verbose_name="Company", related_name='brands')
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True, verbose_name="UUID")
    name = models.CharField(max_length=255, verbose_name="Name")
    description = models.TextField(null=True, blank=True, verbose_name="Description")

    def __str__(self):
        return self.name

class UnitOfMeasure(TimeStampedModel, SoftDeleteModel):
    company = models.ForeignKey(Company, on_delete=models.DO_NOTHING, verbose_name="Company", related_name='units_of_measure')
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True, verbose_name="UUID")
    name = models.CharField(max_length=255, verbose_name="Name")
    abbreviation = models.CharField(max_length=10, verbose_name="Abbreviation")

    def __str__(self):
        return self.name

class Product(TimeStampedModel, SoftDeleteModel):
    company = models.ForeignKey(Company, on_delete=models.DO_NOTHING, verbose_name="Company", related_name='products')
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True, verbose_name="UUID")
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=False, verbose_name="Brand", related_name='products')
    unit_of_measure = models.ForeignKey(UnitOfMeasure, on_delete=models.SET_NULL, null=True, blank=False, verbose_name="Unit of Measure", related_name='products')
    sku = models.CharField(max_length=50, null=True, blank=True, verbose_name="SKU")
    barcode = models.CharField(max_length=50, null=True, blank=True, verbose_name="Barcode")
    name = models.CharField(max_length=255, verbose_name="Name")
    description = models.TextField(null=True, blank=True, verbose_name="Description")
    base_cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Base Cost")
    base_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Base Price")
    minimum_sale_unit = models.DecimalField(max_digits=10, decimal_places=3, verbose_name="Minimum Sale Unit")
    minimum_unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Minimum Unit Price")
    stock_quantity = models.IntegerField(verbose_name="Stock Quantity", default=0)
    has_variants = models.BooleanField(default=False, verbose_name="Has Variant")

    def __str__(self):
        return self.name

class ProductCategory(TimeStampedModel, SoftDeleteModel):
    company = models.ForeignKey(Company, on_delete=models.DO_NOTHING, verbose_name="Company", related_name='product_categories')
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True, verbose_name="UUID")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Category", related_name='product_categories')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Product", related_name='product_categories')

class ProductVariant(TimeStampedModel, SoftDeleteModel):
    company = models.ForeignKey(Company, on_delete=models.DO_NOTHING, verbose_name="Company", related_name='product_variants')
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True, verbose_name="UUID")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Product", related_name='product_variants')
    sku = models.CharField(max_length=50, null=True, blank=True, verbose_name="SKU")
    barcode = models.CharField(max_length=50, null=True, blank=True, verbose_name="Barcode")
    name = models.CharField(max_length=255, db_index=True, verbose_name="Name")
    cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Cost")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Price")
    stock_quantity = models.IntegerField(verbose_name="Stock Quantity")

    def __str__(self):
        return self.name

class Image(TimeStampedModel, SoftDeleteModel):
    company = models.ForeignKey(Company, on_delete=models.DO_NOTHING, verbose_name="Company", related_name='images')
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True, verbose_name="UUID")
    url = models.ImageField(upload_to='images/', verbose_name="Image")
    in_use = models.BooleanField(default=False, verbose_name="In Use")

class ProductImage(TimeStampedModel, SoftDeleteModel):
    company = models.ForeignKey(Company, on_delete=models.DO_NOTHING, verbose_name="Company", related_name='product_images')
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True, verbose_name="UUID")
    image = models.ForeignKey(Image, on_delete=models.CASCADE, verbose_name="Image", related_name='product_images')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Product", related_name='product_images')
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Product Variant", related_name='product_images')

class VariantOption(TimeStampedModel, SoftDeleteModel):
    company = models.ForeignKey(Company, on_delete=models.DO_NOTHING, verbose_name="Company", related_name='variant_options')
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True, verbose_name="UUID")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Product", related_name='variant_options')
    name = models.CharField(max_length=255, db_index=True, verbose_name="Name")

    def __str__(self):
        return self.name

class VariantValue(TimeStampedModel, SoftDeleteModel):
    company = models.ForeignKey(Company, on_delete=models.DO_NOTHING, verbose_name="Company", related_name='variant_values')
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True, verbose_name="UUID")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Product", related_name='variant_values')
    option = models.ForeignKey(VariantOption, on_delete=models.CASCADE, verbose_name="Variant Option", related_name='variant_values')
    value = models.CharField(max_length=255, db_index=True, verbose_name="Value")

    def __str__(self):
        return self.value
