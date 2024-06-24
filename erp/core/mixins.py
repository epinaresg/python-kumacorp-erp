from rest_framework import viewsets, permissions, serializers, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response

from core.pagination import BasePagination
from core.models import Company
from core.services import UtilService

class BaseModelViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = BasePagination
    lookup_field = 'uuid'
    filter_backends = [DjangoFilterBackend]

    def get_company(self):
        company_uuid = self.request.headers.get('X-Company-UUID')
        company = UtilService.validate_uuid(uuid=company_uuid, model_class=Company)
        return company

    def get_queryset(self):
        company_uuid = self.request.headers.get('X-Company-UUID')
        company = UtilService.validate_uuid(uuid=company_uuid, model_class=Company)
        return self.queryset.filter(company=company)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        validated_data['company'] = self.get_company()

        model = self.serializer_class.Meta.model
        UtilService.validate_if_name_is_used('create', validated_data, model)

        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        validated_data['company'] = instance.company

        model = self.serializer_class.Meta.model
        UtilService.validate_if_name_is_used('update', validated_data, model, instance)

        serializer.save()

        return Response(serializer.data)

class BaseSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        excluded_fields = ['id', 'created', 'modified', 'deleted_at', 'restored_at', 'company']
        for field in excluded_fields:
            self.fields.pop(field, None)
