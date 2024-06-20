from django.db import models
from django_extensions.db.models import TimeStampedModel
from django_softdelete.models import SoftDeleteModel
from django.contrib.auth.models import User
import uuid

class Company(TimeStampedModel, SoftDeleteModel):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, verbose_name="UUID")
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="User")
    name = models.CharField(max_length=255, verbose_name="Name")
    settings = models.JSONField(default=dict, verbose_name="Settings")

    def __str__(self):
        return self.name

class Partner(TimeStampedModel, SoftDeleteModel):
    company = models.ForeignKey(Company, on_delete=models.DO_NOTHING, blank=False, null=False, verbose_name="Company")
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
    company = models.ForeignKey(Company, on_delete=models.DO_NOTHING, blank=False, null=False, verbose_name="Company")
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True, verbose_name="UUID")
    name = models.CharField(max_length=255, verbose_name="Name")
    description = models.TextField(null=True, blank=True, verbose_name="Description")
    parent = models.ForeignKey('self', related_name='children', on_delete=models.CASCADE, null=True, blank=True, verbose_name="Parent Category")

    def __str__(self):
        return self.name

class Brand(TimeStampedModel, SoftDeleteModel):
    company = models.ForeignKey(Company, on_delete=models.DO_NOTHING, blank=False, null=False, verbose_name="Company")
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True, verbose_name="UUID")
    name = models.CharField(max_length=255, verbose_name="Name")
    description = models.TextField(null=True, blank=True, verbose_name="Description")

    def __str__(self):
        return self.name

class UnitOfMeasure(TimeStampedModel, SoftDeleteModel):
    company = models.ForeignKey(Company, on_delete=models.DO_NOTHING, blank=False, null=False, verbose_name="Company")
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True, verbose_name="UUID")
    name = models.CharField(max_length=255, verbose_name="Name")
    abbreviation = models.CharField(max_length=10, verbose_name="Abbreviation")

    def __str__(self):
        return self.name

class Product(TimeStampedModel, SoftDeleteModel):
    company = models.ForeignKey(Company, on_delete=models.DO_NOTHING, blank=False, null=False, verbose_name="Company")
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True, verbose_name="UUID")
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=False, verbose_name="Brand")
    unit_of_measure = models.ForeignKey(UnitOfMeasure, on_delete=models.SET_NULL, null=True, blank=False, verbose_name="Unit of Measure")
    sku = models.CharField(max_length=50, null=True, blank=True, verbose_name="SKU")
    barcode = models.CharField(max_length=50, null=True, blank=True, verbose_name="Barcode")
    name = models.CharField(max_length=255, verbose_name="Name")
    description = models.TextField(null=True, blank=True, verbose_name="Description")
    base_cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Base Cost")
    base_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Base Price")
    minimum_sale_unit = models.DecimalField(max_digits=10, decimal_places=3, verbose_name="Minimum Sale Unit")
    minimum_unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Minimum Unit Price")
    stock_quantity = models.IntegerField(verbose_name="Stock Quantity", default=0)
    has_variant = models.BooleanField(default=False, verbose_name="Has Variant")

    def __str__(self):
        return self.name

class ProductCategory(TimeStampedModel, SoftDeleteModel):
    company = models.ForeignKey(Company, on_delete=models.DO_NOTHING, blank=False, null=False, verbose_name="Company")
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True, verbose_name="UUID")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Category")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Product")

class ProductVariant(TimeStampedModel, SoftDeleteModel):
    company = models.ForeignKey(Company, on_delete=models.DO_NOTHING, blank=False, null=False, verbose_name="Company")
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True, verbose_name="UUID")
    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE, verbose_name="Product")
    sku = models.CharField(max_length=50, null=True, blank=True, verbose_name="SKU")
    barcode = models.CharField(max_length=50, null=True, blank=True, verbose_name="Barcode")
    name = models.CharField(max_length=255, verbose_name="Name")
    cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Cost")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Price")
    stock_quantity = models.IntegerField(verbose_name="Stock Quantity")

    def __str__(self):
        return self.name

class ProductImage(TimeStampedModel, SoftDeleteModel):
    company = models.ForeignKey(Company, on_delete=models.DO_NOTHING, blank=False, null=False, verbose_name="Company")
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True, verbose_name="UUID")
    image = models.ImageField(upload_to='product_images/', verbose_name="Image")
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE, verbose_name="Product")
    product_variant = models.ForeignKey(ProductVariant, related_name='images', on_delete=models.CASCADE, null=True, blank=True, verbose_name="Product Variant")

class VariantOption(TimeStampedModel, SoftDeleteModel):
    company = models.ForeignKey(Company, on_delete=models.DO_NOTHING, blank=False, null=False, verbose_name="Company")
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True, verbose_name="UUID")
    product = models.ForeignKey(Product, related_name='variant_options', on_delete=models.CASCADE, verbose_name="Product")
    name = models.CharField(max_length=255, verbose_name="Name")

    def __str__(self):
        return self.name

class VariantValue(TimeStampedModel, SoftDeleteModel):
    company = models.ForeignKey(Company, on_delete=models.DO_NOTHING, blank=False, null=False, verbose_name="Company")
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True, verbose_name="UUID")
    product = models.ForeignKey(Product, related_name='variant_values', on_delete=models.CASCADE, verbose_name="Product")
    option = models.ForeignKey(VariantOption, related_name='values', on_delete=models.CASCADE, verbose_name="Variant Option")
    value = models.CharField(max_length=255, verbose_name="Value")

    def __str__(self):
        return self.name
