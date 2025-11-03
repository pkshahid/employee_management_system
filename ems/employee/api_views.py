# views.py

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import F
from .models import DynamicFormFields, EmployeeData
from .serializers import (
    DynamicFormFieldSerializer,
    EmployeeDataSerializer,
    EmployeeCreateUpdateSerializer,
    EmployeeCreateSerializer,
)

class DynamicFormFieldViewSet(viewsets.ModelViewSet):
    queryset = DynamicFormFields.objects.all().order_by('field_order')
    serializer_class = DynamicFormFieldSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['put'])
    def update_order(self, request):
        payload = request.data
        field = DynamicFormFields.objects.filter(id=payload.get('id')).first()
        if field:
            DynamicFormFields.objects.filter(field_order__gte=int(payload["field_order"])).update(field_order = F('field_order')+1)
            field.field_order = int(payload["field_order"])
            field.save()
        return Response({'detail': 'Order updated successfully'})
    

    @action(detail=False, methods=['post'])
    def add_field(self, request):
        payload = request.data
        if not any([payload.get('field_label'),payload.get('field_type')]):
            return Response({'detail': 'Expected a field label and field type'}, status=status.HTTP_400_BAD_REQUEST)
        field_label = payload.get('field_label')
        field_type = payload.get('field_type')
        field_order = int(payload.get('field_order',"0"))
        field_is_required = payload.get('field_is_required',False)
        options = ''
        if field_type in ['select','radio']:
            options = payload.get('options')
            if isinstance(options,list):
                options = ','.join(options)
        DynamicFormFields.objects.filter(field_order__gte=field_order).update(field_order = F('field_order')+1)
        DynamicFormFields.objects.create(
            field_label = field_label,
            field_type = field_type,
            field_order = field_order,
            field_is_required=field_is_required,
            extra = {'options':options}
        )
        return Response({'detail': 'Field added successfully'})


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = EmployeeData.objects.select_related('uid').all().order_by('-id')
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return EmployeeCreateSerializer
        elif self.request.method in ['PUT', 'PATCH']:
            return EmployeeCreateUpdateSerializer
        return EmployeeDataSerializer