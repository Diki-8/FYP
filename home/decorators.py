from django.contrib import messages
from django.shortcuts import redirect

def custom_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.info(request, "You must be logged in to access this page.")
            return redirect('signin')  # Name of your login URL
        return view_func(request, *args, **kwargs)
    return wrapper