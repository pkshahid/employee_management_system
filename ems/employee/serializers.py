from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import DynamicFormFields, EmployeeData

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class DynamicFormFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = DynamicFormFields
        fields = ['id', 'field_label', 'field_type', 'field_is_required', 'field_order', 'extra', 'created_on', 'updated_on']

class EmployeeDataSerializer(serializers.ModelSerializer):
    uid = UserSerializer()

    class Meta:
        model = EmployeeData
        fields = ['id', 'uid', 'employee_id', 'created_on', 'updated_on', 'extra_data']

class EmployeeCreateUpdateSerializer(serializers.ModelSerializer):
    # accepts uid.pk or nested user data
    uid = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    class Meta:
        model = EmployeeData
        fields = ['id', 'uid', 'employee_id', 'extra_data']



class EmployeeCreateSerializer(serializers.Serializer):
    # User fields
    username = serializers.CharField(max_length=150)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField()


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        dynamic_fields = DynamicFormFields.objects.all().order_by('field_order')

        for field in dynamic_fields:
            field_name = field.field_label.lower().replace(" ", "_")
            field_type = field.field_type.lower()

            if field_type == "text":
                self.fields[field_name] = serializers.CharField(required=field.field_is_required)
            elif field_type == "number":
                self.fields[field_name] = serializers.IntegerField(required=field.field_is_required)
            elif field_type == "checkbox":
                self.fields[field_name] = serializers.BooleanField(required=field.field_is_required)
            elif field_type == "date":
                self.fields[field_name] = serializers.DateField(required=field.field_is_required)
            elif field_type in ["select","radio"]:
                choice_list = field.extra.get('options', '').split(",")
                choices = [(x,x) for x in choice_list]
                self.fields[field_name] = serializers.ChoiceField(choices=choices, required=field.field_is_required)

    def create(self, validated_data):
        # Extract user data
        user_data = {
            'username': validated_data.pop('username'),
            'first_name': validated_data.pop('first_name'),
            'last_name': validated_data.pop('last_name'),
            'email': validated_data.pop('email'),
        }
        password = validated_data.pop('password')

        # Create user
        user = User.objects.create(**user_data)
        user.set_password(password)
        user.save()

        employee_id = validated_data.pop('employee_id','')
        extra_data = validated_data

        # Create EmployeeData record
        employee = EmployeeData.objects.create(
            uid=user,
            employee_id = employee_id,
            extra_data = extra_data
            )
        return employee

    def to_representation(self, instance):
        """Custom representation to avoid DRF trying to read 'username' etc. directly from EmployeeData."""
        return {
            "id": instance.id,
            "employee_id": instance.employee_id,
            "dynamic_fields": instance.extra_data,
            "user": {
                "id": instance.uid.id,
                "username": instance.uid.username,
                "first_name": instance.uid.first_name,
                "last_name": instance.uid.last_name,
                "email": instance.uid.email,
            },
            "created_on": instance.created_on,
            "updated_on": instance.updated_on,
        }
    