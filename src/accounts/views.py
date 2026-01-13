from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site

from .forms import UserRegistrationForm, UserLoginForm, UserUpdateForm
from .tokens import account_activation_token

User = get_user_model()


# -------------------------------
# Register user (with email confirmation)
# -------------------------------
def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True  # disable account until email confirmation
            user.save()

            # Send activation email
            current_site = get_current_site(request)
            mail_subject = 'Activate your CashOnly eCommerce account'
            message = render_to_string('accounts/activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            email = EmailMessage(mail_subject, message, to=[user.email])
            email.send()

            messages.success(request, 'Account created! Check your email to activate your account.')
            return redirect('accounts:login')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


# -------------------------------
# Login user
# -------------------------------
def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                messages.success(request, f'Welcome, {user.username}!')
                return redirect('accounts:profile', username=user.username)
            else:
                messages.error(request, 'Invalid credentials or inactive account.')
    else:
        form = UserLoginForm()
    return render(request, 'accounts/login.html', {'form': form})


# -------------------------------
# Logout user
# -------------------------------
def logout_view(request):
    logout(request)
    messages.success(request, 'You have successfully logged out!')
    return redirect('accounts:login')


# -------------------------------
# User profile / update
# -------------------------------
@login_required
def profile_view(request, username):
    if request.user.username != username:
        messages.error(request, "You can't view someone else's profile.")
        return redirect('accounts:profile', username=request.user.username)

    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('accounts:profile', username=request.user.username)
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})


# -------------------------------
# Activate account via email
# -------------------------------
def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        messages.success(request, "Your account has been activated and you are now logged in!")
        return redirect('accounts:profile', username=user.username)
    else:
        messages.error(request, "Activation link is invalid!")
        return redirect('accounts:login')
