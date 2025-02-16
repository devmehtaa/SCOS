from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

# Login View
def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("menu_home")  # Change "home" to your dashboard or menu page
        else:
            messages.error(request, "Invalid username or password")
    
    return render(request, "login.html")


# Signup View
def signup_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully! You can log in now.")
            return redirect("login")
    else:
        form = UserCreationForm()
    
    return render(request, "signup.html", {"form": form})


# Logout View
def logout_view(request):
    logout(request)
    return redirect("login")


# Password Reset View (Basic - You may extend with Django’s built-in functionality)
def password_reset_view(request):
    return render(request, "password_reset.html")
