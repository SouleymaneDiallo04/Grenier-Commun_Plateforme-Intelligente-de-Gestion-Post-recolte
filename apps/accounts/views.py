"""
Grenier Commun — Vues Authentification
"""
import random
import logging
from datetime import timedelta
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import User, OTPCode

logger = logging.getLogger('apps.accounts')


def connexion(request):
    if request.user.is_authenticated:
        return redirect(request.user.get_dashboard_url())

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            user.derniere_connexion = timezone.now()
            user.save(update_fields=['derniere_connexion'])
            next_url = request.GET.get('next', user.get_dashboard_url())
            return redirect(next_url)
        else:
            messages.error(request, 'Email ou mot de passe incorrect.')

    return render(request, 'accounts/connexion.html')


def deconnexion(request):
    logout(request)
    messages.success(request, 'Vous avez été déconnecté.')
    return redirect('core:accueil')


def inscription(request):
    if request.user.is_authenticated:
        return redirect(request.user.get_dashboard_url())

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        nom = request.POST.get('nom', '').strip()
        prenom = request.POST.get('prenom', '').strip()
        telephone = request.POST.get('telephone', '').strip()
        role = request.POST.get('role', User.AGRICULTEUR)
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        langue = request.POST.get('langue_preferee', 'fr')

        if password1 != password2:
            messages.error(request, 'Les mots de passe ne correspondent pas.')
        elif len(password1) < 8:
            messages.error(request, 'Le mot de passe doit contenir au moins 8 caractères.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Cet email est déjà utilisé.')
        elif role not in [r[0] for r in User.ROLE_CHOICES]:
            messages.error(request, 'Rôle invalide.')
        else:
            user = User.objects.create_user(
                email=email,
                password=password1,
                nom=nom,
                prenom=prenom,
                role=role,
                langue_preferee=langue,
            )
            if telephone:
                try:
                    from phonenumber_field.phonenumber import PhoneNumber
                    user.telephone = PhoneNumber.from_string(telephone, region='SN')
                    user.save(update_fields=['telephone'])
                except Exception:
                    pass

            # Créer profil agriculteur si nécessaire
            if role == User.AGRICULTEUR:
                from apps.core.models import ProfilAgriculteur
                ProfilAgriculteur.objects.get_or_create(user=user)

            login(request, user)
            messages.success(request, f'Bienvenue {prenom} ! Votre compte a été créé.')
            return redirect(user.get_dashboard_url())

    return render(request, 'accounts/inscription.html', {
        'roles': [
            (User.AGRICULTEUR, 'Agriculteur'),
            (User.ACHETEUR, 'Acheteur'),
        ],
        'langues': {'fr': 'Français', 'en': 'English', 'wo': 'Wolof'},
    })


def verifier_otp(request):
    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        telephone = request.POST.get('telephone', '').strip()
        try:
            otp = OTPCode.objects.filter(
                telephone=telephone, code=code, est_utilise=False
            ).latest('cree_le')
            if otp.est_valide():
                otp.est_utilise = True
                otp.save(update_fields=['est_utilise'])
                otp.user.is_verified = True
                otp.user.save(update_fields=['is_verified'])
                messages.success(request, '✅ Téléphone vérifié avec succès.')
                return redirect(otp.user.get_dashboard_url())
            else:
                messages.error(request, 'Code expiré. Demandez un nouveau code.')
        except OTPCode.DoesNotExist:
            messages.error(request, 'Code incorrect.')
    return render(request, 'accounts/verifier_otp.html')


@login_required
def profil(request):
    if request.method == 'POST':
        request.user.nom = request.POST.get('nom', request.user.nom)
        request.user.prenom = request.POST.get('prenom', request.user.prenom)
        request.user.langue_preferee = request.POST.get('langue_preferee', request.user.langue_preferee)
        if 'avatar' in request.FILES:
            request.user.avatar = request.FILES['avatar']
        request.user.save()
        messages.success(request, '✅ Profil mis à jour.')
        return redirect('accounts:profil')
    return render(request, 'accounts/profil.html', {
        'langues': {'fr': 'Français', 'en': 'English', 'wo': 'Wolof'},
    })
