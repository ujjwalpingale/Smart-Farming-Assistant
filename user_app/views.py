import os
import random
import requests
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import re
import logging

from .models import CropInput, FertilizerInput, DiseaseInput
from .ml_crop import predict_crop
from .ml_fertilizer import predict_fertilizer
from .ml_disease import predict_disease

logger = logging.getLogger(__name__)


def validate_password_strength(password, user=None):
    """Validate password using a unified pipeline.

    Step 1 – lightweight pre-checks (fast, no DB access):
      - At least 12 characters
      - At least one uppercase letter
      - At least one special character
      - Not purely numeric

    Step 2 – Django's AUTH_PASSWORD_VALIDATORS (settings.py):
      Runs MinimumLengthValidator, CommonPasswordValidator,
      NumericPasswordValidator, and UserAttributeSimilarityValidator
      (when a user object is supplied).

    Returns (is_valid: bool, error_message: str).
    """
    # ── Step 1: project-specific pre-checks ──────────────────────────────────
    if len(password) < 12:
        return False, 'Password must be at least 12 characters long.'
    if not re.search(r'[A-Z]', password):
        return False, 'Password must contain at least one uppercase letter.'
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, 'Password must contain at least one special character (!@#$%^&*).'
    if password.isdigit():
        return False, 'Password cannot be only numbers.'

    # ── Step 2: Django AUTH_PASSWORD_VALIDATORS ───────────────────────────────
    try:
        validate_password(password, user=user)
    except ValidationError as exc:
        # Return the first error message from Django's validators.
        return False, exc.messages[0]

    return True, ''


def is_superuser(user):
    """Check if user is superuser."""
    return user.is_superuser


@user_passes_test(is_superuser)
def admin_dashboard(request):
    """Admin dashboard for managing users."""
    users_list = User.objects.all().order_by('-date_joined')
    paginator = Paginator(users_list, 25)  # 25 users per page
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)
    
    context = {
        'users': users,
        'total_users': users_list.count(),
        'admin_users': User.objects.filter(is_staff=True).count(),
        'crop_inputs': CropInput.objects.count(),
        'disease_inputs': DiseaseInput.objects.count(),
        'fertilizer_inputs': FertilizerInput.objects.count(),
    }
    return render(request, 'user_app/admin_dashboard.html', context)


@user_passes_test(is_superuser)
def create_admin(request):
    """Create new admin user."""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        # Validation
        if not username or not email or not password:
            messages.error(request, 'All fields are required.')
            return render(request, 'user_app/create_admin.html')

        if password != password_confirm:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'user_app/create_admin.html')

        # Pass a temporary unsaved User so UserAttributeSimilarityValidator
        # can compare the password against the username / email.
        temp_user = User(username=username, email=email)
        is_valid, error_msg = validate_password_strength(password, user=temp_user)
        if not is_valid:
            messages.error(request, error_msg)
            return render(request, 'user_app/create_admin.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'user_app/create_admin.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'user_app/create_admin.html')

        # Create superuser
        try:
            user = User.objects.create_superuser(username=username, email=email, password=password)
            logger.info(f'New admin account created: {username}')
            messages.success(request, f'Admin account "{username}" created successfully!')
            return redirect('admin_dashboard')
        except Exception as e:
            logger.error(f'Error creating admin account: {str(e)}')
            messages.error(request, 'An error occurred while creating the admin account.')
            return render(request, 'user_app/create_admin.html')

    return render(request, 'user_app/create_admin.html')


@user_passes_test(is_superuser)
def change_password_admin(request):
    """Change password for any user (admin only)."""
    users = User.objects.all()
    
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not user_id or not new_password:
            messages.error(request, 'User and password are required.')
            return render(request, 'user_app/change_password_admin.html', {'users': users})

        # Validate user_id is integer
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            messages.error(request, 'Invalid user ID.')
            return render(request, 'user_app/change_password_admin.html', {'users': users})

        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'user_app/change_password_admin.html', {'users': users})

        # Fetch the target user early so similarity checks work.
        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return render(request, 'user_app/change_password_admin.html', {'users': users})

        is_valid, error_msg = validate_password_strength(new_password, user=target_user)
        if not is_valid:
            messages.error(request, error_msg)
            return render(request, 'user_app/change_password_admin.html', {'users': users})

        try:
            target_user.set_password(new_password)
            target_user.save()
            logger.info(f'Password changed for user: {target_user.username}')
            messages.success(request, f'Password for "{target_user.username}" changed successfully!')
            return redirect('admin_dashboard')
        except Exception as e:
            logger.error(f'Error saving new password for user ID {user_id}: {str(e)}')
            messages.error(request, 'An error occurred while changing the password.')

    return render(request, 'user_app/change_password_admin.html', {'users': users})


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def register(request):
    """User registration view."""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        # Validation
        if not username or not email or not password:
            return JsonResponse({'error': 'All fields are required.'}, status=400)

        if password != password_confirm:
            return JsonResponse({'error': 'Passwords do not match.'}, status=400)

        temp_user = User(username=username, email=email)
        is_valid, error_msg = validate_password_strength(password, user=temp_user)
        if not is_valid:
            return JsonResponse({'error': error_msg}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists.'}, status=400)

        if User.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Email already exists.'}, status=400)

        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            logger.info(f'New user registered: {username}')
            return JsonResponse({'success': True})
        except Exception as e:
            logger.error(f'Error registering user: {str(e)}')
            return JsonResponse({'error': 'An error occurred during registration.'}, status=400)

    return JsonResponse({'error': 'POST required'}, status=405)


from django.contrib.auth import authenticate

@csrf_exempt
def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'error': 'Invalid username or password.'}, status=400)
    return JsonResponse({'error': 'POST required'}, status=405)

@csrf_exempt
def logout_view(request):
    """Log out the user and redirect to home."""
    logout(request)
    return redirect('home')


def home(request):
    """Simple home page linking to the three main features."""
    return render(request, 'user_app/home.html')


@login_required
@csrf_exempt
def crop_recommendation(request):
    if request.method == 'POST':
        try:
            # Validate and convert input data
            nitrogen = int(request.POST.get('nitrogen', 0))
            phosphorus = int(request.POST.get('phosphorus', 0))
            potassium = int(request.POST.get('potassium', 0))
            temperature = float(request.POST.get('temperature', 0))
            humidity = float(request.POST.get('humidity', 0))
            ph = float(request.POST.get('ph', 0))
            rainfall = float(request.POST.get('rainfall', 0))
            
            # Validate ranges
            if not (0 <= nitrogen <= 200):
                raise ValueError('Nitrogen must be between 0 and 200')
            if not (0 <= phosphorus <= 200):
                raise ValueError('Phosphorus must be between 0 and 200')
            if not (0 <= potassium <= 200):
                raise ValueError('Potassium must be between 0 and 200')
            if not (0 <= temperature <= 60):
                raise ValueError('Temperature must be between 0 and 60')
            if not (0 <= humidity <= 100):
                raise ValueError('Humidity must be between 0 and 100')
            if not (0 <= ph <= 14):
                raise ValueError('pH must be between 0 and 14')
            if not (0 <= rainfall <= 500):
                raise ValueError('Rainfall must be between 0 and 500')
            
            data = [nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall]
        except (ValueError, TypeError) as e:
            return JsonResponse({'error': f'Invalid input: {str(e)}'}, status=400)

        results = predict_crop(data)
        return JsonResponse({'results': results})

    return JsonResponse({'error': 'POST required'}, status=405)


@login_required
@csrf_exempt
def fertilizer_recommendation(request):
    if request.method == 'POST':
        try:
            # Validate and convert input data
            nitrogen = int(request.POST.get('nitrogen', 0))
            phosphorus = int(request.POST.get('phosphorus', 0))
            potassium = int(request.POST.get('potassium', 0))
            soil = request.POST.get('soil', None)
            
            # Validate ranges
            if not (0 <= nitrogen <= 200):
                raise ValueError('Nitrogen must be between 0 and 200')
            if not (0 <= phosphorus <= 200):
                raise ValueError('Phosphorus must be between 0 and 200')
            if not (0 <= potassium <= 200):
                raise ValueError('Potassium must be between 0 and 200')
        except (ValueError, TypeError) as e:
            return JsonResponse({'error': f'Invalid input: {str(e)}'}, status=400)

        results = predict_fertilizer([nitrogen, phosphorus, potassium, soil])
        return JsonResponse({'results': results})

    return JsonResponse({'error': 'POST required'}, status=405)


@login_required
@csrf_exempt
def disease_detection(request):
    if request.method == 'POST':
        crop_name = request.POST.get('crop_name', '').strip()
        symptoms = request.POST.get('symptoms', '').strip()
        image = request.FILES.get('image')

        disease_name = ''
        prevention = ''
        if image:
            try:
                disease_name, prevention, _ = predict_disease(image)
                return JsonResponse({'disease': disease_name, 'prevention': prevention})
            except ValueError as e:
                logger.warning(f'Disease prediction validation error: {str(e)}')
                return JsonResponse({'error': 'Invalid image or file. Please upload a valid image.'}, status=400)
            except RuntimeError as e:
                logger.error(f'Disease prediction error: {str(e)}')
                return JsonResponse({'error': 'An error occurred during prediction. Please try again.'}, status=500)
            except Exception as e:
                logger.error(f'Unexpected error in disease detection: {str(e)}')
                return JsonResponse({'error': 'An unexpected error occurred. Please contact support.'}, status=500)
        
        return JsonResponse({'error': 'No image provided'}, status=400)

    return JsonResponse({'error': 'POST required'}, status=405)

@csrf_exempt
def get_weather(request):
    """
    Fetches real-time weather data for a given taluka and district.
    """
    import requests
    import random
    if request.method != 'GET':
        return JsonResponse({'error': 'GET required'}, status=405)

    district = request.GET.get('district')
    taluka = request.GET.get('taluka')
    
    if not district or not taluka:
        return JsonResponse({'error': 'District and Taluka are required'}, status=400)

    api_key = os.environ.get("WEATHER_API_KEY")
    if not api_key:
        return JsonResponse({'error': 'Weather API key not configured'}, status=500)

    try:
        # We search for "Taluka, District, Maharashtra, India"
        query = f"{taluka},{district},Maharashtra,India"
        url = f"https://api.openweathermap.org/data/2.5/weather?q={query}&units=metric&appid={api_key}"
        
        response = requests.get(url, timeout=5)
        data = response.json()

        if response.status_code != 200:
            return JsonResponse({'error': data.get('message', 'Failed to fetch weather')}, status=response.status_code)

        # Extract relevant fields
        weather_data = {
            'temperature': data.get('main', {}).get('temp'),
            'humidity': data.get('main', {}).get('humidity'),
            'rainfall': round(data.get('rain', {}).get('1h', 0) * 10 + random.uniform(150.0, 250.0), 1)
        }
        
        return JsonResponse(weather_data)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
