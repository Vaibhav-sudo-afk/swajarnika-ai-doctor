# Swajarnika - Modern Healthcare Management Platform

<div align="center">
    
```ascii
    🏥 S W A J A R N I K A 🏥
    Modern Healthcare Platform
    
    [Patients] <----> [Platform] <----> [Doctors]
       └─Data─────────Security────────Services┘
```

</div>

## Overview
Swajarnika (स्वजर्निका) is a comprehensive healthcare management platform designed to bridge the gap between healthcare providers and patients. The name "Swajarnika" symbolizes enlightenment in healthcare, combining "Swa" (self) and "Jarana" (understanding), aiming to make healthcare services more accessible, efficient, and technologically advanced.

### Project Architecture
```ascii
┌──────────────────────────────────────┐
│            Django Backend            │
├──────────────────────────────────────┤
│ ┌─────────┐  ┌─────────┐ ┌────────┐ │
│ │ Patient │  │ Doctor  │ │  Admin │ │
│ │ Portal  │  │ Portal  │ │ Panel  │ │
│ └────┬────┘  └────┬────┘ └────┬───┘ │
│      │            │           │      │
│ ┌────┴────────────┴───────────┴────┐ │
│ │         Django REST API          │ │
│ └────┬────────────┬───────────┬────┘ │
│      │            │           │      │
│ ┌────┴────┐ ┌────┴─────┐ ┌───┴────┐ │
│ │Database │ │File Store│ │Security│ │
│ └─────────┘ └──────────┘ └────────┘ │
└──────────────────────────────────────┘

## 🎯 Project Aim
The primary goal of Swajarnika is to revolutionize the healthcare management system by:
- Streamlining doctor-patient interactions
- Digitizing medical records and prescriptions
- Enhancing patient care through technology
- Making healthcare more accessible and organized
- Providing a seamless experience for both healthcare providers and patients

## 🚀 Key Features

### For Doctors
- **Digital Visit Management**: Create and manage patient visits digitally
- **Prescription Management**: Easy prescription writing with medication tracking
- **Test Orders**: Digital test requisitions and results management
- **Patient History**: Comprehensive view of patient medical history
- **File Management**: Secure storage and management of medical documents
- **Dashboard**: Intuitive interface for practice management

### For Patients
- **Medical Records**: Access to complete medical history
- **Prescription Access**: Digital access to prescriptions
- **Test Results**: Easy access to medical test results
- **Appointment Management**: Schedule and manage appointments
- **Secure Communication**: Direct communication channel with healthcare providers

### Technical Features
- **Secure Authentication**: Role-based access control
- **Document Management**: Support for multiple file formats
- **Responsive Design**: Works seamlessly across devices
- **Data Security**: Advanced encryption and security measures
- **Scalable Architecture**: Built for growth and expansion

## 🛠️ Technical Stack & Implementation Details

### Backend Architecture
```python
# Core Django Configuration
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'rest_framework',
    'django_allauth',
    'dj_rest_auth',
    'core',  # Main application
]

# Custom User Model
class User(AbstractUser):
    user_type = models.CharField(max_length=20)
    specialty = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50)

# API View Example
class PatientViewSet(viewsets.ModelViewSet):
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Patient.objects.filter(doctor=self.request.user)
```

### Database Schema
```sql
-- Key Database Tables
CREATE TABLE doctors (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    specialty VARCHAR(100),
    license_number VARCHAR(50)
);

CREATE TABLE patients (
    id INTEGER PRIMARY KEY,
    doctor_id INTEGER,
    name VARCHAR(100),
    medical_history TEXT,
    FOREIGN KEY (doctor_id) REFERENCES doctors(id)
);
```

### Security Implementation
```python
# Security Middleware Configuration
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
]

# JWT Authentication Setup
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}
```

### Frontend Architecture
```javascript
// Core JavaScript Functionality
class PatientManager {
    async fetchPatientData(patientId) {
        const response = await fetch(`/api/patients/${patientId}/`);
        return await response.json();
    }
    
    async updateMedicalRecord(patientId, data) {
        return await fetch(`/api/medical-records/`, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
}
```

```html
<!-- Template Structure Example -->
<div class="patient-dashboard">
    <div class="medical-history">
        {% for record in medical_records %}
            <div class="record-card">
                <h3>{{ record.date }}</h3>
                <p>{{ record.diagnosis }}</p>
                <div class="prescriptions">
                    {% for prescription in record.prescriptions %}
                        <!-- Prescription details -->
                    {% endfor %}
                </div>
            </div>
        {% endfor %}
    </div>
</div>
```

### Technology Stack Details
#### Backend Core
- **Framework**: Django 5.0.4
  - Full MVT architecture
  - Custom user model
  - Advanced middleware configuration
- **REST API**: Django REST Framework 3.14.0
  - ViewSets for CRUD operations
  - Custom permissions
  - Serializer validation
- **Database**: 
  - Development: SQLite
  - Production: PostgreSQL
  - Migration management
  - Query optimization
- **Authentication**: 
  - JWT with django-allauth
  - Custom authentication backends
  - Role-based permissions
- **File Processing**: 
  - PyPDF2 for report generation
  - Pillow for image processing
  - Secure file handling
- **API Documentation**: 
  - Swagger UI with drf-yasg
  - Interactive API testing
  - Automated documentation

#### Frontend Technologies
- **Template Engine**: Django Templates
  - Custom template tags
  - Context processors
  - Block-level inheritance
- **Styling**: 
  - Bootstrap 5
  - Custom SCSS architecture
  - Responsive grid system
- **JavaScript**: 
  - ES6+ features
  - Async/Await patterns
  - Module bundling
- **UI Components**:
  - Custom form elements
  - Interactive charts
  - Real-time updates

### Security Features
- CSRF Protection
- Session Security
- File Upload Validation
- Secure Password Handling
- Role-based Access Control

## 💡 Innovation & Differentiation

### What Sets Swajarnika Apart
1. **Integrated Approach**
   - Unified platform for all healthcare management needs
   - Seamless integration between different modules
   - Focus on user experience for both doctors and patients

2. **Technology-First Solution**
   - Modern tech stack ensuring longevity
   - API-ready architecture for future expansion
   - Mobile-responsive design for accessibility

3. **Scalability Focus**
   - Modular architecture for easy feature addition
   - Cloud-ready deployment configuration
   - Performance optimization built-in

## 🔄 Future Roadmap

### Short-term Goals
- Integration with popular EHR systems
- Mobile application development
- Advanced analytics dashboard
- Telehealth consultation features
- AI-powered health insights

### Long-term Vision
- Multi-language support
- International market expansion
- Integration with wearable devices
- Machine learning for predictive healthcare
- Blockchain for medical records

## 📈 Scalability Plan

### Technical Scalability
- Microservices architecture adoption
- Container deployment with Docker
- Load balancing implementation
- Database sharding strategies
- CDN integration for static files

### Business Scalability
- Multi-tenant architecture
- White-label solutions
- API marketplace
- Partner integration system
- Custom deployment options

## 🔐 Security & Compliance

- HIPAA compliance readiness
- GDPR compliance framework
- Regular security audits
- Data encryption at rest and in transit
- Regular backup systems

## 🌟 Unique Value Propositions

1. **Patient-Centric Design**
   - Intuitive user interface
   - Simplified medical record access
   - Educational resources integration

2. **Doctor Efficiency Tools**
   - Quick prescription generation
   - Digital test ordering
   - Automated report generation

3. **Data Intelligence**
   - Health trend analysis
   - Treatment effectiveness tracking
   - Population health insights

## 📦 Installation & Development Guide

### Prerequisites
- Python 3.11+
- Git
- Visual Studio Code (recommended)
- MySQL or PostgreSQL (optional for production)

### Step-by-Step Installation

1. **Clone and Setup Environment**
```bash
# Clone the repository
git clone https://github.com/yourusername/swajarnika.git
cd swajarnika

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On Unix/MacOS

# Install dependencies
pip install -r requirements.txt
```

2. **Environment Configuration**
Create a `.env` file in the root directory:
```env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
```

3. **Database Setup**
```bash
# Initialize database
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

4. **Run Development Server**
```bash
python manage.py runserver
```

5. **Running Tests**
```bash
# Run all tests
python manage.py test

# Run specific test case
python manage.py test core.tests.TestPatientViews
```

### Development Workflow

1. **Code Style Guide**
```python
# Follow PEP 8 guidelines
def get_patient_history(patient_id: int) -> dict:
    """
    Retrieve patient history with associated records.
    
    Args:
        patient_id (int): The patient's unique identifier
        
    Returns:
        dict: Patient history data
    """
    try:
        return Patient.objects.get(id=patient_id).history.all()
    except Patient.DoesNotExist:
        raise Http404("Patient not found")
```

2. **Git Workflow**
```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "feat: add new feature description"

# Push changes
git push origin feature/new-feature
```

3. **API Development**
```python
# Example API endpoint
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def patient_records(request, patient_id):
    try:
        patient = Patient.objects.get(id=patient_id)
        serializer = PatientSerializer(patient)
        return Response(serializer.data)
    except Patient.DoesNotExist:
        return Response(status=404)
```

### Production Deployment

1. **Server Requirements**
- Ubuntu 20.04 LTS or newer
- Nginx
- Gunicorn
- PostgreSQL
- Redis (for caching)

2. **Deployment Commands**
```bash
# Collect static files
python manage.py collectstatic

# Run migrations
python manage.py migrate --no-input

# Start Gunicorn
gunicorn healthcare_platform.wsgi:application --bind 0.0.0.0:8000
```

3. **Nginx Configuration**
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /path/to/swajarnika;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}
```

## 🤝 Contributing
We welcome contributions to Swajarnika! Please read our contributing guidelines and code of conduct before submitting pull requests.

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Team
- Project Lead: [Name]
- Backend Developers: [Names]
- Frontend Developers: [Names]
- UI/UX Designers: [Names]
- Quality Assurance: [Names]

## 📝 API Documentation

### Authentication
```python
# Login endpoint
POST /api/auth/login/
{
    "username": "doctor@example.com",
    "password": "secure_password"
}

# Response
{
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
        "id": 1,
        "email": "doctor@example.com",
        "user_type": "doctor"
    }
}
```

### Patient Management
```python
# Create patient record
POST /api/patients/
{
    "name": "John Doe",
    "date_of_birth": "1990-01-01",
    "medical_history": "No prior conditions"
}

# Get patient details
GET /api/patients/{id}/
```

### Medical Records
```python
# Add medical record
POST /api/records/
{
    "patient_id": 1,
    "diagnosis": "Common cold",
    "prescription": [
        {
            "medicine": "Paracetamol",
            "dosage": "500mg",
            "frequency": "Twice daily"
        }
    ]
}
```

## 🔍 Troubleshooting Guide

### Common Issues

1. **Database Migration Issues**
```bash
# Reset migrations
python manage.py reset_db  # Warning: This will delete all data
python manage.py makemigrations
python manage.py migrate
```

2. **Static Files Not Loading**
```python
# Check settings.py
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
```

3. **API Authentication Errors**
```python
# Verify JWT token
from rest_framework_simplejwt.tokens import AccessToken

token = AccessToken.for_user(user)
print(f"Token valid until: {token['exp']}")
```

## 📞 Contact & Support

### Technical Support
- Email: support@swajarnika.com
- Developer Documentation: https://docs.swajarnika.com
- API Reference: https://api.swajarnika.com/docs

### Community
- GitHub Issues: https://github.com/swajarnika/healthcare-platform/issues
- Discord Community: https://discord.gg/swajarnika
- Stack Overflow Tag: #swajarnika

### Business Inquiries
- Email: business@swajarnika.com
- Phone: +1 (XXX) XXX-XXXX
- LinkedIn: https://linkedin.com/company/swajarnika

---

<div align="center">

Made with ❤️ by the Swajarnika Team

[Website](https://swajarnika.com) • [Documentation](https://docs.swajarnika.com) • [GitHub](https://github.com/swajarnika)

</div>
