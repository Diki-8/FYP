from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib import messages  
from datetime import datetime
from home.models import Contact, Dog
from django.utils import timezone
from home.forms import BookingForm
from home.models import TimeSlot, Booking
from django.contrib.auth.decorators import user_passes_test
from .decorators import custom_login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

def index(request):
    context = {
        "variable": "this is sent"
    }
    return render(request, 'index.html', context)

def about(request):
    return render(request, 'about.html')

def services(request):
    return render(request, 'services.html')

def daycare(request):
    return render(request, 'daycare.html')

def petgrooming(request):
    return render(request, 'petgrooming.html')

def boarding(request):
    return render(request, 'boarding.html')

from django.shortcuts import render, redirect
from django.contrib import messages
from home.models import Contact

import re
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

def contact(request):
    print(f"Request method: {request.method}")  # Debug
    if request.method == "POST":
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        message = request.POST.get('message', '').strip()

        print(f"Name: {name}, Email: {email}, Message: {message}")  # Debug

        # Basic field validations
        if len(name) > 122 or len(email) > 122:
            print("Validation failed: Name or email too long")
            messages.error(request, "Name or email is too long (max 122 characters).")
            return render(request, 'contact.html')

        # Validate name
        if not re.match(r"^[A-Za-z\s'-]{2,}$", name):
            messages.error(request, "Please enter a valid name (only letters, spaces, hyphens).")
            return render(request, 'contact.html')
        
        # Prevent too short messages
        if len(message) < 10:
            messages.error(request, "Message is too short. Please write more details.")
            return render(request, 'contact.html')

        # Detect spammy content
        url_count = len(re.findall(r'(https?://\S+)', message))
        if url_count > 2:
            messages.error(request, "Too many links in your message. Please limit to 2 links.")
            return render(request, 'contact.html')

        # Check for garbage text (repeated same character or very low diversity)
        if len(set(message.lower())) < 5:
            messages.error(request, "Message appears to be spammy. Please write meaningful content.")
            return render(request, 'contact.html')

        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Please enter a valid email address.")
            return render(request, 'contact.html')

        # Save the contact
        if name and email and message:
            try:
                contact = Contact(name=name, email=email, message=message)
                contact.save()
                print("Contact saved successfully")
                messages.success(request, "Your message has been sent successfully!")
                return redirect('contact')
            except Exception as e:
                print(f"Error saving contact: {str(e)}")
                messages.error(request, f"Error saving message: {str(e)}")
        else:
            print("Validation failed: Missing fields")
            messages.error(request, "All fields are required!")

    return render(request, 'contact.html')

    
def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You have been successfully logged in!")
            return redirect('home') 
        else:
            messages.error(request, "Invalid username or password!")
            return redirect('signin') 
    return render(request, 'signin.html')



def signup(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Check if passwords match
        if password1 != password2:
            messages.error(request, "Passwords do not match!")
            return render(request, "signup.html", {
                'show_error_modal': True,
                'prefill_username': username,
                'prefill_email': email
            })

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken! Please choose a different one.")
            return render(request, "signup.html", {
                'show_error_modal': True,
                'prefill_username': username,
                'prefill_email': email
            })

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return render(request, "signup.html", {
                'show_error_modal': True,
                'prefill_username': username,
                'prefill_email': email
            })

        # Validate password strength
        try:
            validate_password(password1)
        except ValidationError as e:
            for error in e:
                messages.error(request, error)
            return render(request, "signup.html", {
                'show_error_modal': True,
                'prefill_username': username,
                'prefill_email': email
            })

        # Create the user
        try:
            user = User.objects.create_user(username=username, email=email, password=password1)
            messages.success(request, "Your account has been created successfully! Please sign in.")
            return redirect("signin")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return render(request, "signup.html", {
                'show_error_modal': True,
                'prefill_username': username,
                'prefill_email': email
            })

    return render(request, "signup.html")


def user_logout(request):
    logout(request)
    messages.success(request, "You have been successfully logged out!")
    return redirect('home')



@custom_login_required
def userprofile(request):
    dogs = Dog.objects.filter(owner=request.user)
    bookings = Booking.objects.filter(user=request.user).order_by('-date')[:3]
    return render(request, 'userprofile.html', {
        'dogs': dogs,
        'recent_bookings': bookings
    })

@custom_login_required
def mybookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-date')
    return render(request, 'bookinglist.html', {'bookings': bookings})

@custom_login_required
@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    all_bookings = Booking.objects.all().order_by('-date')
    return render(request, 'adminpanel.html', {'all_bookings': all_bookings})

@custom_login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if booking.status == 'confirmed':
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, "Booking cancelled successfully")
    else:
        messages.error(request, "Cannot cancel this booking")
    return redirect('mybookings')



@custom_login_required
@user_passes_test(lambda u: u.is_staff)
def admin_cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.status = 'cancelled'
    booking.save()
    messages.success(request, "Booking cancelled successfully")
    return redirect('adminpanel')

@custom_login_required
@user_passes_test(lambda u: u.is_staff)
def admin_complete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.status = 'completed'
    booking.save()
    messages.success(request, "Booking marked as completed")
    return redirect('adminpanel')

@custom_login_required
@user_passes_test(lambda u: u.is_staff)
def admin_undo_cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if booking.status == 'cancelled':
        booking.status = 'confirmed'  # or whatever default "active" status you use
        booking.save()
        messages.success(request, "Booking has been restored successfully!")
    else:
        messages.warning(request, "Only cancelled bookings can be restored.")
    return redirect('adminpanel')  # or whatever your dashboard view is named

@custom_login_required
def booking_grooming(request):
    available_slots = TimeSlot.objects.filter(service_type='grooming')
    
    if request.method == 'POST':
        dog_name = request.POST.get('dog_name')
        dog_breed = request.POST.get('dog_breed')
        dog_size = request.POST.get('dog_size')
        dog_age = request.POST.get('dog_age')
        health_notes = request.POST.get('health_notes')
        service_type = 'grooming'
        time_slot_id = request.POST.get('time_slot')
        grooming_services = request.POST.getlist('grooming_services')  # Get list of selected services
        special_requests = request.POST.get('special_requests', '')

        try:
            # Check if dog exists, or create a new one
            dog, created = Dog.objects.get_or_create(
                owner=request.user,
                name=dog_name,
                defaults={
                    'breed': dog_breed,
                    'age': dog_age if dog_age else None,
                    'size': dog_size if dog_size else '',
                    'special_notes': health_notes if health_notes else ''
                }
            )
            # If dog already exists, update size and special_notes if provided
            if not created:
                if dog_size:
                    dog.size = dog_size
                if health_notes:
                    dog.special_notes = health_notes
                dog.save()

            time_slot = TimeSlot.objects.get(id=time_slot_id)

            # Combine grooming services with special requests
            grooming_services_str = f"Grooming Services: {', '.join(grooming_services)}"
            combined_requests = f"{grooming_services_str}\n{special_requests}" if special_requests else grooming_services_str

            booking = Booking.objects.create(
                user=request.user, 
                dog=dog,
                service=service_type,
                date=request.POST.get('date'),
                time_slot=time_slot,
                special_requests=combined_requests,
                status='confirmed'
            )

            messages.success(request, "Grooming appointment confirmed!")
            return redirect('mybookings')
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")

    return render(request, 'booking_grooming.html', {'available_slots': available_slots})

@custom_login_required
def booking_daycare(request):
    if request.method == 'POST':
        dog_name = request.POST.get('dog_name').strip().title()  # Normalize name
        dog_breed = request.POST.get('dog_breed')
        dog_age = request.POST.get('dog_age')
        dog_size = request.POST.get('dog_size')
        health_notes = request.POST.get('health_notes')
        service_type = 'daycare'
        daycare_duration = request.POST.get('daycare_duration')  # Capture duration

        try:
            # Check if dog exists, or create a new one
            dog, created = Dog.objects.get_or_create(
                owner=request.user,
                name=dog_name,
                defaults={
                    'breed': dog_breed,
                    'age': dog_age if dog_age else None,
                    'size': dog_size if dog_size else '',
                    'special_notes': health_notes if health_notes else ''
                }
            )
            # If dog already exists, update size and special_notes if provided
            if not created:
                if dog_size:
                    dog.size = dog_size
                if health_notes:
                    dog.special_notes = health_notes
                dog.save()

            # Combine duration with special requests
            duration_map = {
                '1': '1 Hour',
                '4': '4 Hours',
                '8': 'Full Day (8hr)'
            }
            duration_text = f"Duration: {duration_map.get(daycare_duration, 'Unknown')}"
            special_requests = request.POST.get('special_requests', '')
            combined_requests = f"{duration_text}\n{special_requests}" if special_requests else duration_text

            booking = Booking.objects.create(
                user=request.user,
                dog=dog,
                service=service_type,
                date=request.POST.get('date'),
                time_slot=None,  # Explicitly set to None for daycare
                special_requests=combined_requests,
                status='confirmed'
            )

            messages.success(request, "Daycare reservation confirmed!")
            return redirect('mybookings')
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")

    return render(request, 'booking_daycare.html')

@custom_login_required
def booking_boarding(request):
    if request.method == 'POST':
        dog_name = request.POST.get('dog_name').strip().title()  # Normalize name
        dog_breed = request.POST.get('dog_breed')
        dog_age = request.POST.get('dog_age')
        dog_size = request.POST.get('dog_size')
        health_notes = request.POST.get('health_notes')
        service_type = 'boarding'
        boarding_duration = request.POST.get('boarding_duration')  # Capture duration

        try:
            # Check if dog exists, or create a new one
            dog, created = Dog.objects.get_or_create(
                owner=request.user,
                name=dog_name,
                defaults={
                    'breed': dog_breed,
                    'age': dog_age if dog_age else None,
                    'size': dog_size if dog_size else '',
                    'special_notes': health_notes if health_notes else ''
                }
            )
            # If dog already exists, update size and special_notes if provided
            if not created:
                if dog_size:
                    dog.size = dog_size
                if health_notes:
                    dog.special_notes = health_notes
                dog.save()

            # Combine duration with special requests
            duration_map = {
                '1': '1 Day',
                '7': '1 Week',
                '30': '1 Month'
            }
            duration_text = f"Duration: {duration_map.get(boarding_duration, 'Unknown')}"
            special_requests = request.POST.get('special_requests', '')
            combined_requests = f"{duration_text}\n{special_requests}" if special_requests else duration_text

            booking = Booking.objects.create(
                user=request.user,
                dog=dog,
                service=service_type,
                date=request.POST.get('date'),
                time_slot=None,  # Explicitly set to None for boarding
                special_requests=combined_requests,
                status='confirmed'
            )

            messages.success(request, "Boarding reservation confirmed!")
            return redirect('mybookings')
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")

    return render(request, 'booking_boarding.html')





@custom_login_required
def booking_details(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, 'booking_details.html', {'booking': booking})


@custom_login_required
def edit_profile(request):
    if request.method == "POST":
        user = request.user
        user.username = request.POST["username"]
        user.email = request.POST["email"]
        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect("userprofile")  

    return render(request, "edit_profile.html")



@custom_login_required
@user_passes_test(lambda u: u.is_staff)
def contact_admin_view(request):
    contacts = Contact.objects.all().order_by('-date')
    return render(request, 'contact_admin.html', {'contacts': contacts})