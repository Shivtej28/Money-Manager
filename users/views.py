from django.shortcuts import render, redirect
from .forms import UserRegisterForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required

# Create your views here.


def register(request):
    print("HHellllooooo")
    if request.method == "POST":
        print("In IF")
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            print("IS Valid")
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = User.objects.create_user(username=username, password=password)
            messages.success(request, f"Account created for {username}!")
            print(user)
            auth_login(request, user)  # Auto-login after registration
            print("Success")
            return redirect("banks")
    else:
        print("IN ELse")
        form = UserRegisterForm()

    return render(request, "users/register.html", {"form": form})


def user_login(request):
    error_message = None
    if request.method == "POST":
        print("In Login")
        form = AuthenticationForm(request.POST)

        print("Is valid")
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        print(username, password)
        if user is not None:
            print(user)
            auth_login(request, user)
            print("Go to profile")
            next_url = request.POST.get("next") or request.GET.get("next") or "banks"
            print(next_url)
            return redirect(next_url)
        else:
            error_message = "Invalid credentials"
            print(error_message)
    else:
        error_message = "Invalid Method"
        form = AuthenticationForm()
    return render(request, "users/login.html", {"form": form})


@login_required
def profile(request):
    return render(request, "users/profile.html")


def user_logout(request):
    if request.method == "POST":
        logout(request)
        return redirect("login")
    else:
        return redirect("profile")
