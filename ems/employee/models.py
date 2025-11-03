from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.

USER_MODEL = get_user_model()

FORM_FIELD_TYPES = [
    ("select","Select"),
    ("text","Text"),
    ("number","Number"),
    ("checkbox","Checkbox"),
    ("radio","Radio"),
    ("date","Date"),
    ("email","Email"),
    ("password","Password"),
]

'''
Model to store employee data
'''
class EmployeeData(models.Model):
    uid = models.ForeignKey(USER_MODEL,null=False,blank=False, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=15,null=False,blank=False)
    created_on = models.DateTimeField(null=False,blank=False,auto_now_add=True)
    updated_on = models.DateTimeField(null=False,blank=False,auto_now=True)
    extra_data = models.JSONField(default=dict)


    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f"{self.uid.username} - {self.employee_id}"


'''
Model to store Dynamic field info
'''
class DynamicFormFields(models.Model):
    field_label = models.CharField(max_length=200,null=False,blank=False)
    field_type = models.CharField(max_length=50,null=False,blank=False,choices=FORM_FIELD_TYPES)
    field_is_required = models.BooleanField(default=False)
    field_order = models.IntegerField(null=False,blank=False)
    extra = models.JSONField(default=dict)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ['field_order', 'id']

    def __str__(self):
        return f"{self.field_label} ({self.field_type})"