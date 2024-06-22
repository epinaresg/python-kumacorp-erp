from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, serializers
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend

from .pagination import BasePagination
from .models import (Category, Company)


class BaseModelViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = BasePagination
    lookup_field = 'uuid'
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        company_uuid = self.request.headers.get('X-Company-UUID')
        company = get_object_or_404(Company, uuid=company_uuid)
        return self.queryset.filter(company=company)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['action'] = self.action
        context['instance'] = self.get_object() if self.action == 'update' else None
        return context


class BaseListSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        excluded_fields = ['id', 'created', 'modified', 'deleted_at', 'restored_at', 'company']
        for field in excluded_fields:
            self.fields.pop(field, None)


class BaseModelSerializer(serializers.ModelSerializer):
    def validate_uuid(self, uuid_value, model_class):
        if uuid_value:
            instance = get_object_or_404(model_class, uuid=uuid_value)
            return instance
        return None

    def validate_company(self):
        request = self.context.get('request')
        company_uuid = request.headers.get('X-Company-UUID')
        company = self.validate_uuid(company_uuid, Company)
        return company

    def validate_if_name_is_used(self, company, validated_data):
        model = self.Meta.model
        action = self.context.get('action')

        if model == Category and 'parent' in validated_data and isinstance(validated_data['parent'], Category):
            name = validated_data['name']
            parent = validated_data['parent']
            queryset = model.objects.filter(name=name, company=company, parent=parent)
            error_message = f"A subcategory with the name '{name}' already exists for this parent."
        else:
            name = validated_data['name']
            queryset = model.objects.filter(name=name, company=company)
            error_message = f"A {model.__name__.lower()} with the name '{name}' already exists."

        instance = self.context.get('instance')

        if action == 'update' and instance:
            queryset = queryset.exclude(pk=instance.pk)

        if queryset.exists():
            raise ValidationError(error_message)

    def create(self, validated_data):
        print('CREATE 3')
        company = self.validate_company()
        validated_data['company'] = company
        self.validate_if_name_is_used(company, validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        company = self.validate_company()
        self.validate_if_name_is_used(company, validated_data)
        validated_data['company'] = company
        return super().update(instance, validated_data)
