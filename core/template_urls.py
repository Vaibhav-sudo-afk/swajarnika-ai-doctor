from django.urls import path
from .views import (
    DoctorRegisterView, DoctorLoginView, PatientRegisterView,
    VisitCreateView, FileUploadView, AIInteractView,
    PatientLoginView, PatientProfileView, LogoutView,
    ChatAPIView,
)

from . import template_views

urlpatterns = [
    # API endpoints
    path('api/doctors/register/',
         DoctorRegisterView.as_view(), name='doctor-register'),
    path('api/doctors/login/', DoctorLoginView.as_view(), name='doctor-login'),
    path('api/patients/register/',
         PatientRegisterView.as_view(), name='patient-register'),
    path('api/patients/login/', PatientLoginView.as_view(), name='patient-login'),
    path('api/patients/profile/',
         PatientProfileView.as_view(), name='patient-profile'),
    path('api/visits/', VisitCreateView.as_view(), name='visit-create'),

    path('api/files/', FileUploadView.as_view(), name='file-upload'),
    path('api/ai/interact/', AIInteractView.as_view(), name='ai-interact'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/chat/', ChatAPIView.as_view(), name='chat_api'),

    # Template views
    path('', template_views.index, name='index'),

    # Doctor URLs
    path('doctor/register/', template_views.doctor_register, name='doctor_register'),
    path('doctor/login/', template_views.doctor_login, name='doctor_login'),
    path('doctor/dashboard/', template_views.doctor_dashboard,
         name='doctor_dashboard'),
    path('doctor/patient/add/', template_views.doctor_patient_add,
         name='doctor_patient_add'),
    path('doctor/patient/<int:patient_id>/',
         template_views.doctor_patient_detail, name='doctor_patient_detail'),
    path('doctor/patient/<int:patient_id>/update/',
         template_views.doctor_patient_update, name='doctor_patient_update'),
    path('doctor/patient/<int:patient_id>/delete/',
         template_views.doctor_patient_delete, name='doctor_patient_delete'),
    path('doctor/patient/<int:patient_id>/visit/add/',
         template_views.doctor_visit_add, name='doctor_visit_add'),
    path('doctor/visit/<int:visit_id>/',
         template_views.doctor_visit_detail, name='doctor_visit_detail'),
    path('doctor/visit/<int:visit_id>/delete/',
         template_views.doctor_visit_delete, name='doctor_visit_delete'),
    path('doctor/patient/<int:patient_id>/file/upload/',
         template_views.doctor_file_upload, name='doctor_file_upload'),
    path('doctor/file/<int:file_id>/delete/',
         template_views.doctor_file_delete, name='doctor_file_delete'),
    path('doctor/visit/<int:visit_id>/update/',
         template_views.doctor_visit_update, name='doctor_visit_update'),
    path('doctor/visit/<int:visit_id>/',
         template_views.doctor_visit_detail, name='doctor_visit_detail'),
    path('doctor/visit/<int:visit_id>/file/upload/',
         template_views.doctor_file_upload, name='doctor_file_upload'),
    # Patient URLs
    path('patient/register/', template_views.patient_register,
         name='patient_register'),
    path('patient/login/', template_views.patient_login, name='patient_login'),
    path('patient/dashboard/', template_views.patient_dashboard,
         name='patient_dashboard'),
    path('patient/visit/<int:visit_id>/',
         template_views.patient_visit_detail, name='patient_visit_detail'),
    path('patient/medications/', template_views.patient_medications,
         name='patient_medications'),
    path('patient/tests/', template_views.patient_tests, name='patient_tests'),
    path('patient/files/', template_views.patient_files, name='patient_files'),

    path('patient/ai-chat/', template_views.patient_ai_chat, name='patient_ai_chat'),

    # Common URLs
    path('logout/', template_views.logout_view, name='logout'),
]
