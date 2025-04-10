from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Doctor, Patient, Visit, Test, Medication, FileUpload, AIPrompt

User = get_user_model()

class DoctorRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = Doctor
        fields = ['id', 'name', 'email', 'specialization', 'phone', 'hospital', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(username=validated_data['email'], password=password, is_doctor=True)
        doctor = Doctor.objects.create(user=user, **validated_data)
        return doctor

class PatientRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['id', 'name', 'date_of_birth', 'gender', 'phone', 'address']

class VisitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visit
        fields = '__all__'

class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = ['id', 'visit', 'test_name', 'region', 'reason', 'result']

class MedicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medication
        fields = ['id', 'visit', 'medication_name', 'reason', 'instructions', 'missed_dose_instructions', 'created_at']

class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileUpload
        fields = ['id', 'visit', 'file_path', 'description']

class AIPromptSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIPrompt
        fields = ['id', 'patient', 'visit', 'prompt_text', 'response_text', 'context_used', 'created_at']

class PatientRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['id', 'name', 'date_of_birth', 'gender', 'phone', 'address', 'password']
        read_only_fields = ['password']