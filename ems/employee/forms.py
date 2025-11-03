from django import forms
from django.contrib.auth import get_user_model
from .models import EmployeeData

USER_MODEL = get_user_model()


'''
Default form for employee creation with default fields
'''
class EmployeeForm(forms.Form):
    username = forms.CharField(max_length=50, required=True)
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=False)
    email = forms.EmailField(required=True)
    employee_id = forms.CharField(max_length=25, required=True)
    password = forms.CharField(required=True, widget=forms.PasswordInput(), min_length=6)

    def __init__(self,*args,**kwargs):
        is_update = kwargs.pop('is_update',None)
        super().__init__(*args,**kwargs)
        if is_update:
            # Remove password field for update
            self.fields.pop('password')

    def save(self):
        data = self.cleaned_data

        # Create user
        user, created = USER_MODEL.objects.update_or_create(
            username=data['username'],
            defaults={
                'first_name': data.get('first_name', ''),
                'last_name': data.get('last_name', ''),
                'email': data.get('email', ''),
            }
        )
        if data.get('password'):
            user.set_password(data['password'])
            user.save()

        # Then Create employee instance
        employee, emp_created = EmployeeData.objects.update_or_create(
            uid=user,
            defaults={
                'employee_id': data.get('employee_id')
            }
        )

        return user, employee