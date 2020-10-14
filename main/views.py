from django.shortcuts import render, redirect
from django.views import View
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.forms.models import model_to_dict
from django.db.models import Sum
from rest_framework.views import APIView
from rest_framework.response import Response
import yfinance as yf
from datetime import datetime, date

from .models import *
from .forms import *
from utils import date_to_timestamp

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


class DashboardView(LoginRequiredMixin, View):
    """
    View to power dashboard.
    Access limited to logged in users only.
    """
    login_url = '/home/'
    def get(self, request):
        """
        Gets all the trade history record for the user which made the request, essentially
        logged in user.

        **Template**
            :template: 'main/dashboard.html'

        **user_account**
            an instance of UserAccount Model
        **trade_history**
            queryset/collection of instances of TradeHistory Model, thus a collection
            of trade history records for the user.

        """
        user_account = UserAcount.objects.get(user=request.user) 
        trade_history = TradeHistory.objects.filter(user=request.user)
        markets = list(Stock.objects.values_list('market', flat=True).distinct())
        stocks  = {}
        for market in markets:
            stocks[market] = list(Stock.objects.filter(market=market).values_list('stock', flat=True).distinct())
        return render(request, 'main/dashboard.html', {'user_account': user_account, 'trade_history': trade_history, 'markets': markets, 'stocks': stocks})

class ManageUsersView(UserPassesTestMixin, View):
    """
    View to handle users management providing functionality to reset user's account.
    Access is limited to users with admin privileeges only.
    """
    def test_func(self):
        """
        Test to make sure the access in limited to users with staff privileges.
        """
        return self.request.user.is_staff

    def get(self, request):
        """
        Renders manage users page with all the users without admin privileges, that is users
        who are going to trade on the website.

        **Template**
            :template: 'main/manage_users.html'

        """
        users = User.objects.filter(is_staff=False)
        return render(request, 'main/manage_users.html', {'users': users})
    
    def post(self, request):
        """
        Handles POST request from manage users page.
        Checks if "reset" button had been clicked first and if found so, will 
        fetch the user id for which reset is supposed to be done from the POST
        data and will reset the account essentially resetting the balance to 
        1000(currently hardcoded, can be made configurable).

        **user_account**
            an instance of UserAccount model.
        """
        if 'reset' in request.POST:
            reset_id = int(request.POST['reset'])
            user = User.objects.get(id=reset_id)
            user_account = UserAcount.objects.filter(user=user)
            if user_account.exists():
                user_account = user_account.first()
                user_account.balance = 1000
                user_account.save()
        return redirect('manage_users')

class ManageStocksView(View):

    def get(self, request):
        stock_form = StockRegistrationForm()
        registered_stocks = Stock.objects.all()
        return render(request, 'main/stock_registration.html', {'stock_form':stock_form, 'registered_stocks': registered_stocks})
    
    def post(self, request):
        if "delete" in request.POST:
            stock_id = int(request.POST['delete'])
            Stock.objects.get(id=stock_id).delete()
            return redirect('manage_stocks')
        else:
            stock_form = StockRegistrationForm(request.POST)
            if stock_form.is_valid():
                stock_form.save()
                return redirect('manage_stocks')
            else:
                return render(request, 'main/stock_registration.html', {'stock_form':stock_form})

class StockAPIView(APIView):
    """
    API to fetch a stock's historical data and return in a structured manner to
    be used in the front-end. API will be using Yahoo Finance data, leveraged using 
    "yfinance" library.
    """
    def get(self, request):
        """
        The API will get the stock name from request data and then get the histoical data 
        for the stock from yfinance. Postprocessing of the fetched data, which happens
        to be a pandas dataframe, involves:
            # Coversion of datetime objects totimestamp
            # rounding all the prices and data to float with two decimal places.
        
        Return:
            ohlc : Arrays of [Date, Open, High, Low, Close]
            volume: Arrays of [Date, Volume]

        Assumption:
            Working with historical data, it is assumed that stock will be traded at last
            trading day's closing price.
        """
        stock = request.GET['stock']
        stock_ticker = yf.Ticker(stock)
        hist = stock_ticker.history(period='30d')
        hist.drop(['Dividends', 'Stock Splits'], axis=1, inplace=True)
        hist['Date'] = hist.index
        ohlc = []
        volume = []
        hist['Date'] = hist['Date'].apply(lambda x: int(datetime.strptime(str(x),'%Y-%m-%d %H:%M:%S').timestamp() * 1000))
        hist['Open'] = hist['Open'].apply(lambda x: round(x, 2))
        hist['High'] = hist['High'].apply(lambda x: round(x, 2))
        hist['Low'] = hist['Low'].apply(lambda x: round(x, 2))
        hist['Close'] = hist['Close'].apply(lambda x: round(x, 2))
        for row in hist.itertuples(index=True, name="Pandas"):
            ohlc.append([row.Date, row.Open, row.High, row.Low, row.Close])
            volume.append([row.Date, row.Volume])
        unit_price = ohlc[-1][4]
        data = {'ohlc': ohlc, 'volume': volume, 'unit_price': unit_price}
        return JsonResponse(data)

class UserStockAPIView(APIView):
    """
    API to fetach User's trade history for a cerating stock.
    Return number of availbale(units) stock for a user.
    """
    def get(self, request):
        """
        Gets the stock for which user details is to be fetched from request data.

        Returns:
            available_units: Number of units of a certain stock available with user
        
        **stocks_trded**
            Collection/Queryset of all the available trade records of the user for the
            requested stock.

        """
        stock = request.GET['stock']
        stocks_traded = TradeHistory.objects.filter(user=request.user, stock=stock)
        bought_stocks = stocks_traded.filter(type="Buy").aggregate(Sum('units'))['units__sum']
        sold_stocks = stocks_traded.filter(type="Sold").aggregate(Sum('units'))['units__sum']
        if sold_stocks:
            available_units = bought_stocks - sold_stocks
        else:
            available_units = bought_stocks
        return JsonResponse({'available_units': available_units})

class UserPortfolioAPIView(APIView):
    """
    Returns user's portfolio data to power portfolio chart on the front-end.
    """
    def get(self, request):
        portfolios = UserPortfolio.objects.filter(user=request.user).order_by('date')
        user_data = [[date_to_timestamp(portfolio.date), portfolio.balance] for portfolio in portfolios]
        return JsonResponse({'portfolio': user_data})

class BuyStocksAPIView(APIView):
    """
    API to handle buying functionality for stocks. This will enter buying record for 
    the user in TradeHistory table and will update the balance.
    Return updated balance for the user and trade details in dictionary form.
    """
    def get(self, request):
        trade = TradeHistory.objects.create(
            user =request.user,
            stock = request.GET['stock'],
            type = 'Buy',
            payment_mode = 'Card',
            payment_description = '*******5264',
            units =  float(request.GET['quantity']),
            unit_price = float(request.GET['unit_price']),
            total_price = float(request.GET['value']),
            date = date.today()
        )
        user_account = UserAcount.objects.get(user=request.user)
        user_account.balance = round((user_account.balance - float(request.GET['value'])), 2)
        user_account.save()
        return JsonResponse({'updated_balance': user_account.balance, 'trade': model_to_dict(trade)})

class SellStocksAPIView(APIView):
    """
    API to handle selling functionality for stocks. This will enter selling record for 
    the user in TradeHistory table and will update the balance.
    Return updated balance for the user and trade details in dictionary form.
    """
    def get(self, request):
        trade = TradeHistory.objects.create(
            user =request.user,
            stock = request.GET['stock'],
            type = 'Sold',
            payment_mode = 'Card',
            payment_description = '*******5264',
            units =  float(request.GET['quantity']),
            unit_price = float(request.GET['unit_price']),
            total_price = float(request.GET['value']),
            date = date.today()
        )
        user_account = UserAcount.objects.get(user=request.user)
        user_account.balance = round((user_account.balance + float(request.GET['value'])), 2)
        user_account.save()
        return JsonResponse({'updated_balance': user_account.balance, 'trade': model_to_dict(trade)})
