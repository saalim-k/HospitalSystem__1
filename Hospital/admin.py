from django.contrib import admin
from .models import Patient,PatientBreast
# Register your models here.
class PatientAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'date_of_birth' )
    field = ['last_name', 'first_name', 'date_of_birth']

@admin.register(PatientBreast)
class PatientBreastAdmin(admin.ModelAdmin):
    list_display = ('id','DateTaken','Patient')
    field = ['id','DateTaken','Patient']

admin.site.register(Patient,PatientAdmin)
admin.site.site_header = 'Breast Cancer Hospital Administration System'