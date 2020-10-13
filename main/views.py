from django.shortcuts import render, redirect
from django.views import View
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

from .models import *


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