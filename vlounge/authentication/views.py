from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

# Login View
def login_view(request):
    if request.method == "POST":
        print("hi")
        username = request.POST["username"]
        password = request.POST["password"]
        print(f"Attempting to authenticate user: {username}")
        user = authenticate(request, username=username, password=password)
        print(f"Result of authenticate(): {user}") 
        if user is not None:
            login(request, user)
            print(f"DEBUG: User logged in: {request.user.is_authenticated}") 
            print(f"DEBUG: User object: {request.user}") 
            return redirect("menu_home")  # Change "home" to your dashboard or menu page
        else:
            messages.error(request, "Invalid username or password")

    print("login view executed")
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
    return redirect("authentication:login")


# Password Reset View 
def password_reset_view(request):
    return render(request, "password_reset.html")

def account_view(request):
    user = request.user

    context = {'username':user.username,
               'last_login':user.last_login,
               'date_joined':user.date_joined
            #    'status':status
               }
    return render(request, "account.html", context)
