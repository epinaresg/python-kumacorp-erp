from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from core.mixins import BaseModelViewSet
from core.filters import BrandFilter, CategoryFilter, PartnerFilter, ProductFilter, UnitOfMeasureFilter
from core.models import Brand, Category, Company, Partner, Product, UnitOfMeasure
from core.serializers import BrandSerializer, CategorySerializer, CompanySerializer, ImageSerializer, PartnerSerializer, ProductSerializer, ProductListSerializer, UnitOfMeasureSerializer
from core.services import CategoryService, CompanyService, ProductService, UtilService

class CompanyViewSet(BaseModelViewSet):
    queryset = Company.objects.all().order_by('-id')
    serializer_class = CompanySerializer
    def get_queryset(self):
        return Company.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        CompanyService.create(user=self.request.user, serializer=serializer)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        CompanyService.update(serializer=serializer)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        return Response({'detail': 'Method "GET" not allowed.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def retrieve(self, request, *args, **kwargs):
        return Response({'detail': 'Method "GET" not allowed.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        return Response({'detail': 'Method "DELETE" not allowed.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        CategoryService.create(company=self.get_company(), serializer=serializer)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        CategoryService.update(serializer=serializer)

        return Response(serializer.data)

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

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related('brand', 'unit_of_measure')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        product_service = ProductService()
        product_service.create(company=self.get_company(), serializer=serializer)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        product_service = ProductService()
        product_service.update(serializer=serializer)

        return Response(serializer.data)

class ImageViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = ImageSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        company_uuid = self.request.headers.get('X-Company-UUID')

        validated_data = serializer.validated_data
        validated_data['company'] = UtilService.validate_uuid(company_uuid, Company)

        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
