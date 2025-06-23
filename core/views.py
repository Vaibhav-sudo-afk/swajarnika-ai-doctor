from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
import openai
from django.contrib.auth import authenticate, login, logout
from .serializers import DoctorRegisterSerializer, PatientRegisterSerializer, VisitSerializer, FileUploadSerializer
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import os
from django.conf import settings
from .models import AIChatMessage, FileUpload, Visit, Patient, Doctor, AIPrompt, Medication, ChatSession
from .utils import format_chat_messages, get_detailed_patient_data, get_file_contents
import tempfile
import uuid
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
import random
import string
import requests
from django.utils import timezone
import traceback
from langdetect import detect
from asgiref.sync import async_to_sync
from django.shortcuts import get_object_or_404
from django.contrib import messages
from .decorators import doctor_required, patient_required
from django.db import transaction
import re
from django.db.models import Q, Count, Max

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
    permission_classes = [IsAuthenticated]

    def post(self, request):
        message = request.data.get('message')
        uploaded_file = request.FILES.get('file')
        session_id = request.data.get('session_id')
        patient = request.user.patient
        action = request.data.get('action')
        confirm_changes = request.data.get('confirm_changes')
        edit_changes = request.data.get('edit_changes')
        import json
        if isinstance(confirm_changes, str):
            try:
                confirm_changes = json.loads(confirm_changes)
            except Exception:
                confirm_changes = None
        if isinstance(edit_changes, str):
            try:
                edit_changes = json.loads(edit_changes)
            except Exception:
                edit_changes = None

        try:
            # Handle session management actions
            if action:
                if not session_id:
                    return Response({'error': 'Session ID required'}, status=400)
                session = ChatSession.objects.get(id=session_id, patient=patient)
                
                if action == 'rename':
                    new_title = request.data.get('title')
                    if not new_title:
                        return Response({'error': 'Title required'}, status=400)
                    session.title = new_title
                    session.save()
                    return Response({'message': 'Session renamed successfully'})
                
                elif action == 'update_category':
                    new_category = request.data.get('category')
                    if not new_category:
                        return Response({'error': 'Category required'}, status=400)
                    session.category = new_category
                    session.save()
                    return Response({'message': 'Category updated successfully'})
                
                elif action == 'update_tags':
                    new_tags = request.data.get('tags')
                    if new_tags is None:
                        return Response({'error': 'Tags required'}, status=400)
                    session.tags = new_tags
                    session.save()
                    return Response({'message': 'Tags updated successfully'})
                
                elif action == 'mark_read':
                    session.mark_as_read()
                    return Response({'message': 'Session marked as read'})
                
                return Response({'error': 'Invalid action'}, status=400)

            # Get or create chat session
            if session_id:
                session = ChatSession.objects.get(id=session_id, patient=patient)
            else:
                session = ChatSession.objects.create(
                    patient=patient,
                    title=f"Chat {timezone.now().strftime('%Y-%m-%d %H:%M')}"
                )

            # Save user message
            user_message = AIChatMessage.objects.create(
                patient=patient,
                session=session,
                message=message,
                is_ai=False
            )

            # Mark session as unread for new messages
            session.mark_as_unread()

            # Handle file if present
            file_content = None
            if uploaded_file:
                file_content = self.process_uploaded_file(uploaded_file, patient)

            # Get historical context for this session
            historical_context = self.get_historical_context(session)

            # Format messages
            messages = format_chat_messages(
                patient=patient,
                user_message=message,
                file_content=file_content,
                historical_context=historical_context
            )

            # Make direct API call without streaming
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
                }
            )

            if response.status_code == 200:
                ai_reply = response.json()['choices'][0]['message']['content']

                # Save AI response
                ai_message = AIChatMessage.objects.create(
                    patient=patient,
                    session=session,
                    message=ai_reply,
                    is_ai=True
                )

                # Save prompt for tracking
                AIPrompt.objects.create(
                    patient=patient,
                    visit=Visit.objects.filter(patient=patient).last(),
                    session=session,
                    prompt_text=message,
                    response_text=ai_reply,
                    context_used=get_detailed_patient_data(patient)[:500]
                )

                # Detect patient info changes
                detected_changes = self.try_update_patient_info(message, patient)
                if detected_changes and not action:
                    # Ask user for confirmation before updating
                    return Response({
                        'message': ai_reply,
                        'detected_changes': detected_changes,
                        'session_id': session.id,
                        'file_processed': bool(uploaded_file),
                        'require_confirmation': True
                    }, status=status.HTTP_200_OK)
                # If user confirms changes
                if action == 'apply_changes' and confirm_changes:
                    with transaction.atomic():
                        for field, value in confirm_changes.items():
                            if field == 'date_of_birth':
                                from datetime import date
                                value = date.fromisoformat(value)
                            setattr(patient, field, value)
                        patient.save()
                    # Update all AIPrompt context_used for this patient (across all sessions)
                    prompts = AIPrompt.objects.filter(patient=patient)
                    for prompt in prompts:
                        prompt.context_used = get_detailed_patient_data(patient)[:500]
                        prompt.save()
                # If user edits changes
                if action == 'edit_changes' and edit_changes:
                    with transaction.atomic():
                        for field, value in edit_changes.items():
                            if field == 'date_of_birth':
                                from datetime import date
                                value = date.fromisoformat(value)
                            setattr(patient, field, value)
                        patient.save()
                    # Update all AIPrompt context_used for this patient (across all sessions)
                    prompts = AIPrompt.objects.filter(patient=patient)
                    for prompt in prompts:
                        prompt.context_used = get_detailed_patient_data(patient)[:500]
                        prompt.save()
                # If user discards, do nothing
                return Response({
                    'message': ai_reply,
                    'session_id': session.id,
                    'file_processed': bool(uploaded_file)
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': f"API Error: {response.status_code}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        """
        List all chat sessions for the patient, or messages for a session if session_id is provided.
        """
        patient = request.user.patient
        session_id = request.query_params.get('session_id')
        search_query = request.query_params.get('search')
        category_filter = request.query_params.get('category')
        tags_filter = request.query_params.get('tags')

        if session_id:
            # Return messages for this session
            session = ChatSession.objects.get(id=session_id, patient=patient)
            messages = AIChatMessage.objects.filter(session=session).order_by('created_at')
            
            # Mark session as read when viewing messages
            session.mark_as_read()
            
            return Response({
                'session_id': session.id,
                'title': session.title,
                'category': session.category,
                'tags': session.tags,
                'started_at': session.started_at,
                'messages': [
                    {
                        'id': msg.id,
                        'is_ai': msg.is_ai,
                        'message': msg.message,
                        'created_at': msg.created_at
                    } for msg in messages
                ]
            })
        else:
            # Build query for sessions
            sessions = ChatSession.objects.filter(patient=patient)
            
            if search_query:
                sessions = sessions.filter(
                    Q(title__icontains=search_query) |
                    Q(messages__message__icontains=search_query)
                ).distinct()
            
            if category_filter:
                sessions = sessions.filter(category=category_filter)
            
            if tags_filter:
                tags_list = [tag.strip() for tag in tags_filter.split(',')]
                for tag in tags_list:
                    sessions = sessions.filter(tags__icontains=tag)
            
            sessions = sessions.annotate(
                message_count=Count('messages'),
                last_message=Max('messages__message')
            ).order_by('-last_message_at')

            return Response({
                'sessions': [
                    {
                        'id': s.id,
                        'title': s.title,
                        'category': s.category,
                        'tags': s.get_tags_list(),
                        'started_at': s.started_at,
                        'last_message': s.last_message,
                        'message_count': s.message_count,
                        'has_unread': s.has_unread,
                        'last_message_at': s.last_message_at
                    } for s in sessions
                ],
                'categories': ChatSession.CATEGORY_CHOICES
            })

    def process_uploaded_file(self, file, patient):
        visit = Visit.objects.filter(patient=patient).order_by('-date_of_visit').first()
        if not visit:
            visit = Visit.objects.create(
                patient=patient,
                doctor=patient.doctor,
                date_of_visit=timezone.now().date(),
                diagnosis="Document Review via Chat",
                treatment_plan="AI Assistant Analysis"
            )
        file_upload = FileUpload.objects.create(
            visit=visit,
            file_path=file,
            description="Uploaded during AI chat consultation"
        )
        return process_file_for_chat(file_upload)

    def get_historical_context(self, session):
        # Get all messages from all sessions for this patient
        all_messages = AIChatMessage.objects.filter(
            patient=session.patient
        ).order_by('created_at')  # Get all messages, ordered by time
        
        # Group messages by session for better context
        context = {'previous_interactions': []}
        current_session_messages = []
        other_sessions_messages = {}  # Dictionary to group messages by session
        
        for msg in all_messages:
            message_data = {
                'prompt': msg.message if not msg.is_ai else '',
                'response': msg.message if msg.is_ai else '',
                'session_id': msg.session.id if msg.session else None,
                'timestamp': msg.created_at.isoformat()
            }
            
            if msg.session and msg.session.id == session.id:
                current_session_messages.append(message_data)
            elif msg.session:
                if msg.session.id not in other_sessions_messages:
                    other_sessions_messages[msg.session.id] = []
                other_sessions_messages[msg.session.id].append(message_data)
        
        # Add current session context first
        context['previous_interactions'].extend(current_session_messages)
        
        # Add context from other sessions, grouped by session
        for session_id, messages in other_sessions_messages.items():
            if messages:
                session_date = ChatSession.objects.get(id=session_id).started_at.strftime('%Y-%m-%d %H:%M')
                context['previous_interactions'].append({
                    'prompt': f'\nContext from chat session {session_id} (started {session_date}):\n',
                    'response': 'Here are the relevant messages from this session:'
                })
                context['previous_interactions'].extend(messages)
        
        return context

    def try_update_patient_info(self, message, patient):
        # Simple regex-based extraction for name, age, gender, phone, address
        changes = {}
        name_match = re.search(r"my name is ([a-zA-Z ]+)", message, re.IGNORECASE)
        age_match = re.search(r"i am (\d{1,3}) ?(years old|yrs old|y/o)?", message, re.IGNORECASE)
        gender_match = re.search(r"i am (male|female|other)", message, re.IGNORECASE)
        phone_match = re.search(r"my phone( number)? is (\d{10,15})", message, re.IGNORECASE)
        address_match = re.search(r"my address is ([^\.\n]+)", message, re.IGNORECASE)
        from datetime import date
        if name_match:
            changes['name'] = name_match.group(1).strip()
        if age_match:
            age = int(age_match.group(1))
            today = date.today()
            dob = date(today.year - age, today.month, today.day)
            changes['date_of_birth'] = dob.isoformat()
        if gender_match:
            changes['gender'] = gender_match.group(1).capitalize()
        if phone_match:
            changes['phone'] = phone_match.group(2)
        if address_match:
            changes['address'] = address_match.group(1).strip()
        return changes


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)


@doctor_required
def doctor_visit_delete(request, visit_id):
    try:
        visit = get_object_or_404(Visit, id=visit_id, doctor=request.user.doctor)
        visit.delete()
        messages.success(request, 'Visit deleted successfully.')
        return JsonResponse({'status': 'success'})
    except Exception as e:
        messages.error(request, f'Error deleting visit: {str(e)}')
        return JsonResponse({'error': str(e)}, status=400)
