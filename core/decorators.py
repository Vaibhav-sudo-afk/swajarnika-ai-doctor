from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from functools import wraps


def doctor_required(view_func):
    """
    Decorator for views that checks that the user is logged in and is a doctor,
    redirecting to the doctor login page if necessary.
    """
    @wraps(view_func)
    @login_required(login_url='doctor_login')
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, 'doctor'):
            return redirect('doctor_login')
        return view_func(request, *args, **kwargs)
    return wrapper


def patient_required(view_func):
    """
    Decorator for views that checks that the user is logged in and is a patient,
    redirecting to the patient login page if necessary.
    """
    @wraps(view_func)
    @login_required(login_url='patient_login')
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, 'patient'):
            return redirect('patient_login')
        return view_func(request, *args, **kwargs)
    return wrapper
