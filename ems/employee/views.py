from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views import View
from django.urls import reverse
import json

from .models import DynamicFormFields, EmployeeData
from .forms import EmployeeForm


'''
Employee form customization view
'''
class EmployeeFormView(View):

    template = "employee/form_config.html"
    form = EmployeeForm

    def get(self, request):
        dynamic_fields = list(DynamicFormFields.objects.all().order_by('field_order').values())

        # prepare options as list for template convenience
        for d in dynamic_fields:
            if d.get('extra') and isinstance(d['extra'], dict):
                opts = d['extra'].get('options', '')
                if isinstance(opts, str):
                    d['options'] = opts
                elif isinstance(opts, list):
                    d['options'] = ','.join(opts)
                else:
                    d['options'] = ''
            else:
                d['options'] = ''

        contexts = {
            "form": self.form(),
            "dynamic_fields": dynamic_fields,
        }
        return render(request, self.template, contexts)

    def post(self, request):
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

        if not data or 'fields' not in data:
            return JsonResponse({"status": "error", "message": "fields missing"}, status=400)

        fields = data['fields']

        # Process deletions and creates/updates
        processed_ids = []
        for f in fields:

            #Delete
            if f.get('deleted') and f.get('id'):
                DynamicFormFields.objects.filter(id=f['id']).delete()
                continue

            fid = f.get('id')
            extra = {}

            if f.get('options'):
                # store options as comma-separated string for backward compatibility
                extra['options'] = f.get('options')

            if fid:
                # update
                DynamicFormFields.objects.filter(id=fid).update(
                    field_label=f.get('label', ''),
                    field_type=f.get('field_type', 'text'),
                    field_is_required=bool(f.get('required', False)),
                    field_order=int(f.get('order', 0)),
                    extra=extra
                )
                processed_ids.append(fid)
            else:
                obj = DynamicFormFields.objects.create(
                    field_label=f.get('label', ''),
                    field_type=f.get('field_type', 'text'),
                    field_is_required=bool(f.get('required', False)),
                    field_order=int(f.get('order', 0)),
                    extra=extra
                )
                processed_ids.append(obj.id)

        return JsonResponse({"status": "success", "message": "Saved Successfully"})

'''
Employee Creation flow
'''
class EmployeeCreationView(View):
    template = "employee/creation_form.html"
    form = EmployeeForm
    is_update = False

    def dispatch(self, request, *args, **kwargs):
        if 'pk' in kwargs and kwargs['pk']:
            self.is_update = True
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, pk=None):
        dynamic_fields_qs = DynamicFormFields.objects.all().order_by('field_order')
        dynamic_fields = []

        for dyn_field in dynamic_fields_qs:
            options = dyn_field.extra.get('options', '') if isinstance(dyn_field.extra, dict) else ''
            opts_list = []

            if isinstance(options, str) and options:
                opts_list = [o.strip() for o in options.split(',') if o.strip()]
            elif isinstance(options, list):
                opts_list = options
                
            dynamic_fields.append({
                'id': dyn_field.id,
                'field_label': dyn_field.field_label,
                'field_type': dyn_field.field_type,
                'field_is_required': dyn_field.field_is_required,
                'options': opts_list,
            })

        initial = {}
        edit_employee = None
        if pk:
            edit_employee = get_object_or_404(EmployeeData, pk=pk)
            # prepare initial values for default fields
            initial = {
                'username': edit_employee.uid.username,
                'first_name': edit_employee.uid.first_name,
                'last_name': edit_employee.uid.last_name,
                'email': edit_employee.uid.email,
                'employee_id': edit_employee.employee_id,
            }

        context = {
            'form': self.form(initial=initial),
            'dynamic_fields': dynamic_fields,
            'edit_employee': edit_employee,
        }
        return render(request, self.template, context)

    def post(self, request, pk=None):
        # Use request.POST for standard fields and collect extras
        data = request.POST.dict()
       

        if data:
            form = self.form(data or None,is_update=self.is_update)
            if form.is_valid():
                user, employee = form.save()
                # save extras
                extra = {}
                for key, value in data.items():
                    if key not in ['username', 'first_name', 'last_name', 'email', 'employee_id', 'password']:
                        extra[key] = value
                employee.extra_data = extra
                employee.save()

                return JsonResponse({"status": "success", "message": "Employee Created/Updated successfully", "id": employee.id})
            else:
                errors = form.errors.get_json_data()
                print(errors)
                return JsonResponse({"status": "error", "message": "Validation errors", "errors": errors}, status=400)
        return JsonResponse({"status": "error", "message": "No data received"}, status=400)

class EmployeeListView(View):
    template = "employee/employee_list.html"
    def get(self, request):
        filter_args = {}
        dynamic_fields = DynamicFormFields.objects.values().all()
        for dyn in dynamic_fields:
            if request.GET.get(dyn['field_label']):
                filter_args[f"extra_data__{dyn['field_label']}"] = request.GET[dyn['field_label']]
            if dyn['field_type'] in ["select","radio"]:
                dyn["options"] = dyn["extra"].get("options","").split(",")
        # server-side search
        employees = EmployeeData.objects.select_related('uid').all()
        print(filter_args)
        employees = employees.filter(**filter_args)

        # pagination
        from django.core.paginator import Paginator
        paginator = Paginator(employees.order_by('-id'), 3)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

                

        context = {'page_obj': page_obj, 'employees': page_obj.object_list,'dynamic_fields':dynamic_fields}
        return render(request, self.template, context)
    
    def delete(self,request,pk):
        if pk:
            employee = EmployeeData.objects.filter(pk=pk).last()
            if employee:
                uid = employee.uid
                uid.delete()
                return JsonResponse({"status":"success"})