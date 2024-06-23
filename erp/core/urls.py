from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import (
    BrandViewSet, CategoryViewSet, CompanyViewSet, ImageViewSet, PartnerViewSet,
    ProductViewSet, UnitOfMeasureViewSet,
)

router = DefaultRouter()
router.register(r'companies', CompanyViewSet)
router.register(r'partners', PartnerViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'brands', BrandViewSet)
router.register(r'units-of-measure', UnitOfMeasureViewSet)
router.register(r'products', ProductViewSet)
router.register(r'upload/images', ImageViewSet, basename='upload-images')

urlpatterns = [
    path('', include(router.urls)),

]
