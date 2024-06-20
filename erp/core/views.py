
from rest_framework.exceptions import PermissionDenied

from .mixins import BaseModelViewSet

from .filters import (
    BrandFilter, CategoryFilter, PartnerFilter, ProductFilter, UnitOfMeasureFilter,
)

from .models import (
    Brand, Category, Company, Partner,
    Product, ProductVariant, ProductImage, UnitOfMeasure,
    VariantOption, VariantValue,
)
from .serializers import (
    BrandSerializer, CategorySerializer, CompanySerializer, PartnerSerializer,
    ProductSerializer, ProductVariantSerializer,
    ProductImageSerializer, UnitOfMeasureSerializer, VariantOptionSerializer, VariantValueSerializer,
)


class CompanyViewSet(BaseModelViewSet):
    queryset = Company.objects.all().order_by('-id')
    serializer_class = CompanySerializer
    def get_queryset(self):
        return Company.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        instance = self.get_object()
        if instance.user != self.request.user:
            raise PermissionDenied("No tienes permiso para editar este registro.")
        serializer.save()


class PartnerViewSet(BaseModelViewSet):
    queryset = Partner.objects.all().order_by('-id')
    serializer_class = PartnerSerializer
    filterset_class = PartnerFilter


class CategoryViewSet(BaseModelViewSet):
    queryset = Category.objects.all().order_by('-id')
    serializer_class = CategorySerializer
    filterset_class = CategoryFilter
    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action in ['list']:
            return queryset.filter(parent__isnull=True)
        return queryset


class BrandViewSet(BaseModelViewSet):
    queryset = Brand.objects.all().order_by('-id')
    serializer_class = BrandSerializer
    filterset_class = BrandFilter


class UnitOfMeasureViewSet(BaseModelViewSet):
    queryset = UnitOfMeasure.objects.all().order_by('-id')
    serializer_class = UnitOfMeasureSerializer
    filterset_class = UnitOfMeasureFilter


class ProductViewSet(BaseModelViewSet):
    queryset = Product.objects.all().order_by('-id')
    serializer_class = ProductSerializer
    filterset_class = ProductFilter


class ProductVariantViewSet(BaseModelViewSet):
    queryset = ProductVariant.objects.all().order_by('-id')
    serializer_class = ProductVariantSerializer


class ProductImageViewSet(BaseModelViewSet):
    queryset = ProductImage.objects.all().order_by('-id')
    serializer_class = ProductImageSerializer


class VariantOptionViewSet(BaseModelViewSet):
    queryset = VariantOption.objects.all().order_by('-id')
    serializer_class = VariantOptionSerializer


class VariantValueViewSet(BaseModelViewSet):
    queryset = VariantValue.objects.all().order_by('-id')
    serializer_class = VariantValueSerializer
