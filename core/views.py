from django.shortcuts import render
from django.contrib.auth.decorators import login_required

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
