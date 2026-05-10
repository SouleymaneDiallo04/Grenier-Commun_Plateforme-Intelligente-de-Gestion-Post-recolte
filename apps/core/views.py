from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def accueil(request):
    if request.user.is_authenticated:
        return redirect(request.user.get_dashboard_url())
    return render(request, 'core/accueil.html')

@login_required
def dashboard_redirect(request):
    return redirect(request.user.get_dashboard_url())
