from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings

from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from .models import Profile


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            profile = user.profile
            token = profile.generate_verification_token()
            send_verification_email(request, user, token)
            login(request, user)
            messages.success(request, 'Registration successful! Please check your email to verify your account.')
            return redirect('home')
    else:
        form = UserRegisterForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def send_verification_email(request, user, token):
    subject = 'Verify your email - Django LMS'
    verification_url = f"{settings.BASE_URL}/accounts/verify/{token}/"
    
    context = {
        'user': user,
        'verification_url': verification_url,
    }
    
    html_message = render_to_string('accounts/email/verification_email.html', context)
    plain_message = f"Hi {user.username},\n\nPlease verify your email by clicking this link:\n{verification_url}\n\nThank you!"
    
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=True,
    )


def verify_email(request, token):
    profile = get_object_or_404(Profile, verification_token=token)
    
    if not profile.is_token_valid():
        messages.error(request, 'This verification link has expired. Please request a new one.')
        return redirect('resend_verification')
    
    if profile.email_verified:
        messages.info(request, 'Your email has already been verified.')
        return redirect('home')
    
    profile.email_verified = True
    profile.verification_token = ''
    profile.save()
    
    messages.success(request, 'Your email has been verified successfully!')
    return redirect('home')


@login_required
def resend_verification(request):
    if request.user.profile.email_verified:
        messages.info(request, 'Your email is already verified.')
        return redirect('home')
    
    if request.method == 'POST':
        token = request.user.profile.generate_verification_token()
        send_verification_email(request, request.user, token)
        messages.success(request, 'Verification email has been sent. Please check your inbox.')
        return redirect('home')
    
    return render(request, 'accounts/resend_verification.html')


def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if not user.profile.email_verified:
                token = user.profile.generate_verification_token()
                send_verification_email(request, user, token)
                messages.error(request, 'Please verify your email first. A new verification email has been sent.')
                return redirect('login')
            
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'accounts/login.html')


def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'accounts/profile.html', context)
