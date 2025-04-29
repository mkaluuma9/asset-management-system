from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from .forms import LoginForm
from django.contrib.auth import authenticate, login

@login_required
def dashboard(request):
    role = request.user.role

    if role == 'admin':
        template = 'admin_dashboard.html'
    elif role == 'supervisor':
        template = 'supervisor_dashboard.html'
    elif role == 'field_agent':
        template = 'field_agent_dashboard.html'
    else:
        template = 'user_dashboard.html'

    return render(request, template, {'user': request.user})



def make_asset_request(request):
    return render(request, 'make_request.html')

def view_assigned_assets(request):
    return render(request, 'view_assets.html')

def make_payment(request):
    return render(request, 'make_payment.html')

# core/views.py



class CoreLoginView(LoginView):
    template_name = 'core/login.html'



def login_view(request):
    form = LoginForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('dashboard')  # Change to your post-login URL
            else:
                form.add_error(None, "Invalid username or password")

    return render(request, 'login.html', {'form': form})

def register_view(request):
    # Logic for the registration view (you might want to include a form)
    return render(request, 'register.html')