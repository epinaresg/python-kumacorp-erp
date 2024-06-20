from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PartnerViewSet, CategoryViewSet, CompanyViewSet, BrandViewSet, UnitOfMeasureViewSet,
    ProductViewSet, ProductVariantViewSet, ProductImageViewSet,
    VariantOptionViewSet, VariantValueViewSet
)

router = DefaultRouter()
router.register(r'companies', CompanyViewSet)
router.register(r'partners', PartnerViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'brands', BrandViewSet)
router.register(r'units-of-measure', UnitOfMeasureViewSet)
router.register(r'products', ProductViewSet)
router.register(r'product-variants', ProductVariantViewSet)
router.register(r'product-images', ProductImageViewSet)
router.register(r'variant-options', VariantOptionViewSet)
router.register(r'variant-values', VariantValueViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
