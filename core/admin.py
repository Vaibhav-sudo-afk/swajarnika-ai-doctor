from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Doctor, Patient, Visit, Test, Medication, FileUpload, AIPrompt, ChatSession

class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {'fields': ('is_doctor', 'is_patient')}),
    )

admin.site.register(User, UserAdmin)
admin.site.register(Doctor)
admin.site.register(Patient)
admin.site.register(Visit)
admin.site.register(Test)
admin.site.register(Medication)
admin.site.register(FileUpload)
admin.site.register(AIPrompt)
admin.site.register(ChatSession)
