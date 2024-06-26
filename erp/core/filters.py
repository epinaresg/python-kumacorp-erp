
from django_filters import rest_framework as filters
from core.models import (
    Brand, Category, Partner, Product, UnitOfMeasure
)

class PartnerFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    email = filters.CharFilter(field_name='email', lookup_expr='icontains')
    tax_id = filters.CharFilter(field_name='tax_id', lookup_expr='icontains')

    class Meta:
        model = Partner
        fields = ['name', 'email', 'tax_id']



class CategoryFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Category
        fields = ['name']



class BrandFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Brand
        fields = ['name']



class UnitOfMeasureFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = UnitOfMeasure
        fields = ['name']



class ProductFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    brand_name = filters.CharFilter(field_name='brand__name', lookup_expr='icontains')
    unit_of_measure_name = filters.CharFilter(field_name='unit_of_measure__name', lookup_expr='icontains')

    class Meta:
        model = Product
        fields = ['name']
