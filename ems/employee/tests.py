from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from .models import DynamicFormFields, EmployeeData


class EmployeeModuleTests(TestCase):
    def setUp(self):
        # Setup users and clients
        self.user = User.objects.create_user(username="admin", password="admin123")
        self.client = Client()
        self.api_client = APIClient()
        self.api_client.force_authenticate(user=self.user)

        # Sample field
        self.field = DynamicFormFields.objects.create(
            field_label="Department",
            field_type="text",
            field_order=1,
            field_is_required=True,
            extra={"options": ""}
        )

    def test_employee_form_view_get(self):
        '''
        Custom Employee Form configuration view render test
        '''

        response = self.client.get(reverse("employee_form_config"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "employee/form_config.html")

    def test_employee_creation_view_get(self):
        '''
        Tests Employee Creation Form loading and rendering.
        '''

        response = self.client.get(reverse("employee_create"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "employee/creation_form.html")

    def test_employee_form_post_invalid_json(self):
        '''
        Employee form configuratio negative test case.
        '''

        response = self.client.post(
            reverse("employee_form_config"),
            data="Invalid JSON",
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    def test_dynamic_form_field_api_list(self):
        '''
        API - Test Dynamic form field fetch test case
        '''
       
        url = reverse("api-fields-list")
        response = self.api_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Department", str(response.data))

    def test_dynamic_form_field_api_add(self):
        '''
        API - Test Dynamic form field add
        '''

        url = reverse("api-fields-add-field")
        data = {"field_label": "Gender", "field_type": "select", "field_order": 2, "options": ["Male", "Female"]}
        response = self.api_client.post(url, data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(DynamicFormFields.objects.count(), 2)

    def test_employee_create_api(self):
        '''
        API - Employee creation positive test case
        '''

        url = reverse("api-employees-list")
        data = {
            "username": "john",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "password": "Str0ng@123",
            "employee_id": "E001",
            "department": "IT"
        }
        response = self.api_client.post(url, data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(EmployeeData.objects.filter(uid__username="john").exists())

    def test_employee_list_view(self):
        '''
        Employee Listing page rendering test.
        '''

        EmployeeData.objects.create(uid=self.user, employee_id="EMP100")
        response = self.client.get(reverse("employee_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "employee/employee_list.html")

    def test_employee_delete_view(self):
        '''
        Employee deletion test.
        '''

        employee = EmployeeData.objects.create(uid=self.user, employee_id="EMP200")
        response = self.client.delete(reverse("employee_list", args=[employee.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="admin").exists())