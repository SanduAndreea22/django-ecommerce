from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm, UserUpdateForm


# -------------------------------
# Register user (no email confirmation - demo project)
# -------------------------------
def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.save()

            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f'Welcome, {user.username}! Your account has been created.')
            return redirect('accounts:profile', username=user.username)
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
                messages.error(request, 'Incorrect username or password.')
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
