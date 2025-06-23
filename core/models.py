from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    is_doctor = models.BooleanField(default=False)
    is_patient = models.BooleanField(default=False)

    def __str__(self):
        if self.is_doctor:
            return f"Doctor: {self.username}"
        elif self.is_patient:
            return f"Patient: {self.username}"
        return self.username

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    specialization = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, unique=True)
    hospital = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='patients', null=True, blank=True)
    name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=20)
    phone = models.CharField(max_length=15, unique=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    password = models.CharField(default='',max_length=100)
    
    def __str__(self):
        return self.name

class Visit(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date_of_visit = models.DateField()
    diagnosis = models.TextField()
    treatment_plan = models.TextField()
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=[('draft', 'Draft'), ('approved', 'Approved')], default='draft')
    approved_by = models.ForeignKey(Doctor, related_name='approved_visits', null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Visit for {self.patient.name} on {self.date_of_visit}"

class Test(models.Model):
    visit = models.ForeignKey(Visit, on_delete=models.CASCADE)
    test_name = models.CharField(max_length=255)
    region = models.CharField(max_length=255, blank=True, null=True)
    reason = models.TextField()
    result = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.test_name

class Medication(models.Model):
    visit = models.ForeignKey(Visit, on_delete=models.CASCADE)
    medication_name = models.CharField(max_length=255)
    reason = models.TextField()
    instructions = models.TextField()
    missed_dose_instructions = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.medication_name

class FileUpload(models.Model):
    visit = models.ForeignKey(Visit, on_delete=models.CASCADE)
    file_path = models.FileField(upload_to='uploads/')
    description = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"File for {self.visit}"

class AIPrompt(models.Model):
    REQUIRED_INFO_STATUSES = [
        ('complete', 'Complete Information'),
        ('pending', 'Information Required'),
        ('updated', 'Information Updated')
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    visit = models.ForeignKey(Visit, on_delete=models.CASCADE, null=True, blank=True)
    session = models.ForeignKey('ChatSession', on_delete=models.CASCADE, null=True, blank=True)
    prompt_text = models.TextField(default='')
    response_text = models.TextField(default='')
    context_used = models.TextField(null=True, blank=True)
    language_detected = models.CharField(max_length=50, blank=True, null=True)
    required_info = models.JSONField(default=dict, blank=True)
    info_status = models.CharField(max_length=20, choices=REQUIRED_INFO_STATUSES, default='complete')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"AI Prompt for {self.patient.name} at {self.created_at}"

class ChatSession(models.Model):
    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('symptoms', 'Symptoms'),
        ('medication', 'Medication'),
        ('test_results', 'Test Results'),
        ('follow_up', 'Follow Up'),
        ('emergency', 'Emergency'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='chat_sessions')
    title = models.CharField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    started_at = models.DateTimeField(auto_now_add=True)
    has_unread = models.BooleanField(default=False)
    last_read_by_patient = models.DateTimeField(null=True, blank=True)
    last_message_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title or f'Chat {self.id}'} - {self.patient.name}"

    def mark_as_read(self):
        self.has_unread = False
        self.last_read_by_patient = timezone.now()
        self.save()

    def mark_as_unread(self):
        self.has_unread = True
        self.save()

    def get_tags_list(self):
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]

class AIChatMessage(models.Model):
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE)
    session = models.ForeignKey('ChatSession', on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    message = models.TextField()
    is_ai = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{'AI' if self.is_ai else 'Patient'} message at {self.created_at}"

