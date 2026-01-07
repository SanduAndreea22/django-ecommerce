from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')
    else:
        form = UserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})


from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from cart.views import merge_session_cart_to_user  # importăm funcția de merge

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Mutăm produsele din session la user
            merge_session_cart_to_user(request)

            return redirect('/')  # sau 'cart:cart_detail' dacă vrei să vezi coșul imediat
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})



def logout_view(request):
    logout(request)
    return redirect('/')

@login_required
def profile_view(request):
    profile = request.user.profile  # obține profilul asociat user-ului
    return render(request, 'accounts/profile.html', {'profile': profile})


from django.contrib.auth.decorators import login_required
from .forms import ProfileForm

@login_required
def edit_profile_view(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('accounts:profile')  # redirect la profil după salvare
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'accounts/edit_profile.html', {'form': form})
