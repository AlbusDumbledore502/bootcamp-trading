from django.shortcuts import render, redirect
from django.views import View
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

from .models import *
from .forms import *



# Create your views here.
class HomeView(View):
    """
    View that will power the main/home page.
    """
    def get(self, request):
        """
        Renders home page of the app.

        **Template:**
            :template: 'main/home.html'

        """
        return render(request, 'main/home.html')
    
    def post(self, request):
        """
        Handles POST request for home page, which is essentially login functionality.

        ''user''
            An instance of User model if username and password checks out else None.
        
        If user is an admin user, will be redirected to manage users page, else 
        the user will ve redirected to dashboard.

        """
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect('manage_users')
            else:
                return redirect('dashboard')
        else:
            messages.warning(request, 'Incorrect credentials!')
            return redirect('home')
        return HttpResponse()

class LogoutView(View):
    """
    View to handle logout request.
    """
    def get(self, request):
        logout(request)
        return redirect('home')


class SignUpView(View):
    """
    View to handle sign up.
    """
    def get(self, request):
        """
        Renders the sign up page for new users to sign in.

        **Template**
            :template: 'main/register.html'
        
        **registration_form**
            An instance of UserRegistrationForm(ModelForm bound to User model).

        """
        registration_form = UserRegistrationFrom()
        return render(request, 'main/register.html', {'registration_form': registration_form})
    
    def post(self, request):
        """
        Handles POST request for signup.

        If inputs given by user in the form is valid, a new user will be created
        and the user will be redirected to the home page with success message.

        In case form in invalidated, same form will be renderd with error description.

        """
        registration_form= UserRegistrationFrom(request.POST)
        if registration_form.is_valid():
            user = registration_form.save()
            UserAcount.objects.create(user=user, balance=1000)
            messages.success(request, 'Account cretaed successfully. Please login.')
            return redirect('home')
        else:
            return render(request, 'main/register.html', {'registration_form': registration_form})