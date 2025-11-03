from django.urls import path, include
from .views import EmployeeFormView, EmployeeCreationView, EmployeeListView
from rest_framework import routers
from .api_views import DynamicFormFieldViewSet, EmployeeViewSet

router = routers.DefaultRouter()
router.register(r'api/fields', DynamicFormFieldViewSet, basename='api-fields')
router.register(r'api/employees', EmployeeViewSet, basename='api-employees')

urlpatterns = [
    path('form/config/', EmployeeFormView.as_view(), name='employee_form_config'),
    path('create/', EmployeeCreationView.as_view(), name='employee_create'),
    path('edit/<int:pk>/', EmployeeCreationView.as_view(), name='employee_edit'),
    path('list/', EmployeeListView.as_view(), name='employee_list'),
    path('list/<int:pk>/', EmployeeListView.as_view(), name='employee_list'),
    # API router
    path('', include(router.urls)),
]