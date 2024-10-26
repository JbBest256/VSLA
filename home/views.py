from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import DecimalField
import json
import os
import secrets
from .forms import RegisterForm,LoginForm
from membership.models import Membership
from .models import Notifications
from finance.models import Transaction,FinancialYear,AccountSettings
from django.db.models import Subquery, OuterRef, Max, Value
from django.db.models.functions import Coalesce


@login_required(login_url = 'login')
def Home(request):
   
    
    return render(request, 'home/home/home.html')

def UserLogin(request):
    form = LoginForm()
    if request.method == 'POST':
        print('POST')
        form = LoginForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data.get('phone_number')
            password = form.cleaned_data.get('password')

            user = authenticate(request, phone_number=phone_number, password=password)
            if user is not None:
                login(request, user)
                
                return redirect('home')
            else:
                form.add_error('password', 'Sorry, that login was invalid. Please try again')
    
    return render(request, 'home/home/sign-in.html', {'form': form})


@login_required(login_url = 'login')
def UserLogout(request):
    logout(request)
    return redirect('home')
    
def UserRegister(request):
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            phone_number = form.cleaned_data.get('phone_number')
            password = form.cleaned_data.get('password')
            user = authenticate(request, phone_number=phone_number, password=password)
            
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                form.add_error(None, 'User authentication failed. Please try again.')
        else:
            # Add a generic error if the form is not valid
            form.add_error(None, 'Please correct the errors below and try again.')

    else:
        form = RegisterForm()
    
    return render(request,'home/home/sign-up.html', {'form': form})



def UserProfile(request):
    # Get the active membership for the current user
    try:
        active_membership = Membership.objects.get(member=request.user, active_association=True)
    except Membership.DoesNotExist:
        # Handle the case where no active membership is found
        return render(request, 'home/home/userprofile.html', {'error': 'No active membership found.'})

    # Get the active financial year for the active association
    try:
        active_financial_year = FinancialYear.objects.get(association=active_membership.member_associations, active_status=True)
    except FinancialYear.DoesNotExist:
        # Handle the case where no active financial year is found
        return render(request, 'home/home/userprofile.html', {'error': 'No active financial year found.'})

    # Get the accounts created for the active association and active financial year
    accounts = AccountSettings.objects.filter(
        association=active_membership.member_associations,
        financial_year=active_financial_year
    )

    # Subquery to get the latest transaction for each account filtered by the member
    latest_transaction_subquery = (
        Transaction.objects
        .filter(account=OuterRef('pk'), member=active_membership)  # Filter by the member in the Transaction model
        .order_by('-date')
        .values('balance_after_transaction')[:1]
    )

    # Annotate each account with the latest account balance or default to zero if no transactions exist
    accounts_with_balances = accounts.annotate(
        latest_balance=Coalesce(Subquery(latest_transaction_subquery), Value(0), output_field=DecimalField())
    )

    # Count the number of accounts
    account_count = accounts_with_balances.count()

    # Get the last 10 transactions for the active member, ordered by date in descending order
    last_10_transactions = Transaction.objects.filter(member=active_membership).order_by('-date')[:10]

    return render(request, 'home/home/userprofile.html', {
        'accounts_with_balances': accounts_with_balances,
        'account_count': account_count,
        'active_membership': active_membership,
        'active_financial_year': active_financial_year,
        'last_10_transactions': last_10_transactions,
    })

def EditUserProfile(request):
    #launches user profile
    
    return render(request,'home/home/editprofile.html')
    
    
    



def notifications_view(request):
    notifications = []
    active_association = None

    if request.user.is_authenticated:
        user = request.user

        try:
            # Get the user's active membership
            user_membership = Membership.objects.get(member=user, active_association=True)
            active_association = user_membership.member_associations
        except Membership.DoesNotExist:
            user_membership = None

        if user_membership:
            # Fetch group notifications for the active association
            group_notifications = Notifications.objects.filter(
                added_by__member_associations=active_association,
                is_group_notification=True
            ).order_by('-created_at')

            # Fetch user-specific notifications where is_group_notification is False
            user_notifications = Notifications.objects.filter(
                recipient__member_associations=active_association,
                is_group_notification=False
            ).order_by('-created_at')

            # Combine both querysets
            notifications = group_notifications | user_notifications

            # Order the combined notifications by created_at
            notifications = notifications.order_by('-created_at')

    return render(request, 'home/notification/notifications.html', {
        'notifications': notifications,
        'active_association': active_association,
    })



  