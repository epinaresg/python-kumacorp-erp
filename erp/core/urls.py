from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PartnerViewSet, CategoryViewSet, CompanyViewSet, BrandViewSet, UnitOfMeasureViewSet,
    ProductViewSet,
)

router = DefaultRouter()
router.register(r'companies', CompanyViewSet)
router.register(r'partners', PartnerViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'brands', BrandViewSet)
router.register(r'units-of-measure', UnitOfMeasureViewSet)
router.register(r'products', ProductViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
