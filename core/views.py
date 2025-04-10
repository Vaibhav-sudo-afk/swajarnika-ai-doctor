from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
import openai
from django.contrib.auth import authenticate, login, logout
from .serializers import DoctorRegisterSerializer, PatientRegisterSerializer, VisitSerializer, FileUploadSerializer
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import os
from django.conf import settings
from .models import AIChatMessage, FileUpload, Visit, Patient, Doctor, AIPrompt
from .utils import format_chat_messages, get_detailed_patient_data
import tempfile
import uuid
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
import random
import string
import requests
from django.utils import timezone
import traceback

User = get_user_model()

openai.api_key = "sk-lRtbEbMz_nah_M3s-64K1g"
openai.base_url = "https://chatapi.akash.network/api/v1"

AKASH_API_KEY = "sk-lRtbEbMz_nah_M3s-64K1g"
AKASH_API_ENDPOINT = "https://chatapi.akash.network/api/v1"
REQUEST_TIMEOUT = 20


def make_random_password(length=8):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


class DoctorRegisterView(APIView):
    def post(self, request):
        serializer = DoctorRegisterSerializer(data=request.data)
        if serializer.is_valid():
            doctor = serializer.save()
            return Response({'id': doctor.id, 'message': 'Doctor registered successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DoctorLoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(username=email, password=password)
        if user is not None and getattr(user, 'is_doctor', False):
            login(request, user)
            return Response({'message': 'Login successful'})
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)


class PatientRegisterView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def post(self, request):
        # Ensure the user is a doctor
        if not hasattr(request.user, 'doctor'):
            return Response({'error': 'Only doctors can register patients.'}, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()
        # Generate a secure random password for the patient
        password = make_random_password()
        # You may pass this to the patient in response
        data['password'] = password
        if User.objects.filter(username=data['phone']).exists():
            return Response({'error': 'A user with this phone number already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        # Create a user for the patient
        user = User.objects.create_user(
            username=data['phone'],
            password=password,
            is_patient=True
        )
        serializer = PatientRegisterSerializer(data=data)
        if serializer.is_valid():
            patient = serializer.save(
                user=user, doctor=request.user.doctor, password=password)
            return Response({'patient_id': patient.id, 'generated_password': password}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def create_ai_prompt(visit):
    # Gather diagnosis and medications details
    medications = Medication.objects.filter(visit=visit)
    prompt_text = f"Diagnosis: {visit.diagnosis}\nTreatment: {visit.treatment_plan}\n"
    for med in medications:
        prompt_text += f"Medication: {med.medication_name} - {med.instructions} (Missed dose: {med.missed_dose_instructions})\n"
    AIPrompt.objects.create(patient=visit.patient,
                            visit=visit, prompt=prompt_text)


class VisitCreateView(APIView):
    def post(self, request):
        serializer = VisitSerializer(data=request.data)
        if serializer.is_valid():
            visit = serializer.save()
            create_ai_prompt(visit)  # update AI prompt table
            return Response({'visit_id': visit.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FileUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'File uploaded successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AIInteractView(APIView):
    def post(self, request):
        patient_id = request.data.get('patient_id')
        question = request.data.get('question')

        try:
            # Get the patient
            patient = Patient.objects.get(id=patient_id)

            # Format messages for Akash API
            messages = format_chat_messages(patient, question)

            # Get AI response from Akash API
            answer = query_akash_chat(messages)

            return Response({'answer': answer})
        except Patient.DoesNotExist:
            return Response({'error': 'Patient not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PatientLoginView(APIView):
    def post(self, request):
        phone = request.data.get('phone')
        password = request.data.get('password')

        try:
            user = User.objects.get(username=phone)
        except User.DoesNotExist:
            return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)

        user = authenticate(username=phone, password=password)
        if user is not None and hasattr(user, 'patient'):
            login(request, user)
            return Response({'message': 'Login successful', 'patient_id': user.patient.id}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)


class PatientProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            patient = request.user.patient
            serializer = PatientRegisterSerializer(patient)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({'error': 'Not a patient'}, status=status.HTTP_403_FORBIDDEN)


class ChatAPIView(APIView):
    def get(self, request):
        """Get chat history for the patient"""
        try:
            patient = request.user.patient
            messages = AIChatMessage.objects.filter(patient=patient).order_by('created_at')
            
            return Response({
                'messages': [
                    {
                        'message': msg.message,
                        'is_ai': msg.is_ai,
                        'timestamp': msg.created_at.strftime('%Y-%m-%d %H:%M:%S')
                    } for msg in messages
                ]
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        message = request.data.get('message')
        uploaded_file = request.FILES.get('file')

        if not message and not uploaded_file:
            return Response({'error': 'Message or file is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            patient = request.user.patient

            # Save user message first
            user_message = AIChatMessage.objects.create(
                patient=patient,
                message=message,
                is_ai=False
            )

            # Handle file if present
            if uploaded_file:
                visit = Visit.objects.filter(patient=patient).order_by('-date_of_visit').first()
                if not visit:
                    visit = Visit.objects.create(
                        patient=patient,
                        doctor=patient.doctor,
                        date_of_visit=timezone.now().date(),
                        diagnosis="Chat Upload",
                        treatment_plan="Document Review"
                    )

                file_upload = FileUpload.objects.create(
                    visit=visit,
                    file_path=uploaded_file,
                    description=f"Uploaded during chat: {uploaded_file.name}"
                )

            # Format messages with context
            messages = format_chat_messages(patient, message)

            # Make API request
            response = requests.post(
                "https://chatapi.akash.network/api/v1/chat/completions",
                json={
                    "model": "Meta-Llama-3-1-8B-Instruct-FP8",
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 1024
                },
                headers={
                    "Authorization": "Bearer sk-lRtbEbMz_nah_M3s-64K1g",
                    "Content-Type": "application/json"
                },
                timeout=20
            )

            if response.status_code == 200:
                ai_reply = response.json()['choices'][0]['message']['content']

                # Save AI response
                ai_message = AIChatMessage.objects.create(
                    patient=patient,
                    message=ai_reply,
                    is_ai=True
                )

                # Save prompt for tracking
                AIPrompt.objects.create(
                    patient=patient,
                    visit=visit if uploaded_file else None,
                    prompt_text=message,
                    response_text=ai_reply,
                    context_used=get_detailed_patient_data(patient)[:500]
                )

                return Response({
                    'message': ai_reply,
                    'context_used': True,
                    'file_processed': bool(uploaded_file),
                    'message_id': ai_message.id
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': f"API Error: {response.status_code}",
                    'details': response.text
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
