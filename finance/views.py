from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from decimal import Decimal
from django.db.models import Q
from django.forms.forms import NON_FIELD_ERRORS  # Correct import for NON_FIELD_ERRORS
from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList
from django.db import IntegrityError
from django.db.models import Max
from .forms import FinancialYearForm, AccountSettingsForm, TransactionForm,LoanRequestForm
from .models import FinancialYear, AccountSettings, Transaction,LoanRequest,Guarantor
from association.models import Association
from membership.models import Membership
from home.models import Notifications
# Create your views here.



@login_required
def create_financial_year(request):
    user = request.user
    # Fetch the active association from the Membership model
    member = Membership.objects.filter(member=user, active_association=True).first()
    if not member:
        return render(request, 'error.html', {'message': 'No active association found for this user.'})

    association = member.member_associations

    if request.method == 'POST':
        form = FinancialYearForm(request.POST)
        if form.is_valid():
            # Check if there is an active financial year for the association
            active_year = FinancialYear.objects.filter(association=association, active_status=True).first()
            if active_year:
                # Deactivate the active financial year
                active_year.active_status = False
                active_year.save()

            # Save the new financial year
            financial_year = form.save(commit=False)
            financial_year.association = association
            financial_year.active_status = True  # Mark the new year as active
            financial_year.save()

            # Create a notification for this action
            Notifications.objects.create(
                added_by=member,  # The member performing the action
                
                message=f"New financial year added for {association.name}.",  # A simple message without the member's name
                is_group_notification=True  # This notification is for all group members
            )

            return redirect('financial_year_list')  # Update with your actual URL
    else:
        form = FinancialYearForm()

    return render(request, 'home/finance/create_financial_year.html', {'form': form, 'association': association})


def create_account_settings(request):
    user = request.user
    form_errors = []

    # Get the active association from the user's memberships
    active_membership = Membership.objects.filter(member=user, active_association=True).first()
    if not active_membership:
        form_errors.append("No active membership found.")
    
    active_association = active_membership.member_associations if active_membership else None
    
    # Get the active financial year for the association
    active_financial_year = FinancialYear.objects.filter(
        association=active_association, active_status=True
    ).first() if active_association else None

    if not active_financial_year:
        form_errors.append("No active financial year found for the active association.")

    if request.method == "POST":
        form = AccountSettingsForm(request.POST)

        if form_errors:
            # Ensure form._errors is initialized before assigning errors
            if form._errors is None:
                form._errors = ErrorList()
            form._errors[NON_FIELD_ERRORS] = ErrorList(form_errors)  # Updated this line
        elif form.is_valid():
            account_settings = form.save(commit=False)
            account_settings.association = active_association
            account_settings.financial_year = active_financial_year

            # Check for uniqueness before saving
            if AccountSettings.objects.filter(
                association=active_association, 
                name=account_settings.name, 
                financial_year=active_financial_year
            ).exists():
                form.add_error(None, "Account settings for this name already exist for the selected association and financial year.")
            else:
                try:
                    account_settings.save()
                    messages.success(request, "Account settings created successfully.")
                    
                    # Redirect to the dynamically generated URL of the created account
                    return redirect('view_account', slug=account_settings.slug)
                except IntegrityError:
                    form.add_error(None, "There was a database error. Please try again.")
    else:
        form = AccountSettingsForm()
    if form_errors:
        # Ensure form._errors is initialized before assigning errors
        if form._errors is None:
            form._errors = {}
        form._errors[NON_FIELD_ERRORS] = ErrorList(form_errors)  # Updated this line to use a dict

    return render(request, 'home/finance/create_account_settings.html', {
        'form': form,
        'active_association': active_association,
        'active_financial_year': active_financial_year,
    })


    
    
def view_account(request, slug):
    user = request.user

    # Get the active association of the current user
    active_membership = Membership.objects.filter(member=user, active_association=True).first()
    if not active_membership:
        return render(request, 'error.html', {'message': 'No active association found.'})

    active_association = active_membership.member_associations

    # Ensure that the requested account belongs to the user's active association
    
  
    account = get_object_or_404(AccountSettings, slug=slug, association=active_association)
    transactions = Transaction.objects.filter(account=account).order_by('-date')  # Fetch transactions related to the account

    return render(request, 'home/finance/savings.html',{
        'account': account,
        'transactions': transactions,
    })









def process_transaction(request, slug):
    account = get_object_or_404(AccountSettings, slug=slug)
    active_association = get_active_association(request.user)  # Function to get the active association

    form = TransactionForm(request.POST or None, active_association=active_association)

    if request.method == 'POST' and form.is_valid():
        # Get form data
        membership = form.cleaned_data.get('member')  # This is now a Membership instance
        transaction_type = form.cleaned_data.get('transaction_type')
        transaction_mode = form.cleaned_data.get('transaction_mode')
        transaction_id = form.cleaned_data.get('transaction_id')
        amount = form.cleaned_data.get('amount')
        description = form.cleaned_data.get('description')

        # Calculate the member's current balance
        last_transaction = Transaction.objects.filter(member=membership, account=account).order_by('-date').first()
        member_balance = last_transaction.balance_after_transaction if last_transaction else Decimal(0.00)

        # Calculate the current account balance
        last_account_transaction = Transaction.objects.filter(account=account).order_by('-date').first()
        account_balance = last_account_transaction.account_balance if last_account_transaction else Decimal(0.00)

        # Initialize balance after transaction and shares
        balance_after_transaction = None
        shares = Decimal(0.00)

        # Handle different transaction types
        if transaction_type == 'Deposit':
            if amount < account.minimum_deposit or amount > account.maximum_deposit:
                form.add_error('amount', f"The deposit amount must be between {account.minimum_deposit} and {account.maximum_deposit}.")
            else:
                balance_after_transaction = member_balance + amount
                account_balance += amount  # Add deposit amount to the account balance
                shares = amount / account.share_price

        elif transaction_type == 'Withdrawal':
            # Withdrawal amount must be greater than zero and not more than the member's balance
            if amount <= 0:
                form.add_error('amount', "The withdrawal amount must be greater than zero.")
            elif amount > member_balance:
                form.add_error('amount', "Insufficient funds. The member's balance is lower than the withdrawal amount.")
            else:
                # Deduct the withdrawal amount from both the member balance and account balance
                balance_after_transaction = member_balance - amount
                account_balance -= amount
                # Calculate negative shares for the withdrawal
                shares = -(amount / account.share_price)

        elif transaction_type == 'Expense':
            # Deduct the amount from the account balance only
            account_balance -= amount
            balance_after_transaction = member_balance  # Member's balance remains unchanged

        elif transaction_type == 'Dividend':
            # Deduct the amount from both the account balance and member balance
            balance_after_transaction = member_balance - amount
            account_balance -= amount
            # Shares remain unchanged for dividends

        elif transaction_type == 'Loan':
            # Deduct the loan amount from the account balance only
            account_balance -= amount
            balance_after_transaction = member_balance  # Member's balance remains unchanged

        elif transaction_type == 'Loan Repayment':
            # Add the loan repayment amount back to the account balance
            account_balance += amount
            balance_after_transaction = member_balance  # Member's balance remains unchanged

        else:
            form.add_error('transaction_type', "Invalid transaction type.")

        # If there are no errors, create and save the transaction
        if not form.errors:
            Transaction.objects.create(
                member=membership,  # Use the Membership instance here
                account=account,
                amount=amount,
                transaction_type=transaction_type,
                transaction_mode=transaction_mode,
                transaction_id=transaction_id,
                balance_after_transaction=balance_after_transaction,
                account_balance=account_balance,  # Save the updated account balance
                shares=shares,  # Save the calculated shares (negative for withdrawals, zero for others)
                description=description,
            )
            return redirect('view_account', slug=account.slug)

    return render(request, 'home/finance/add_transaction.html', {'form': form, 'account': account})

def get_active_association(user):
    try:
        return Membership.objects.get(member=user, active_association=True).member_associations
    except Membership.DoesNotExist:
        return None



@login_required
def financial_year_list(request):
    user = request.user
    # Fetch the active association from the Membership model
    member = Membership.objects.filter(member=user, active_association=True).first()
    
    if not member:
        return render(request, 'error.html', {'message': 'No active association found for this user.'})

    association = member.member_associations
    # Get all financial years for the active association
    years = FinancialYear.objects.filter(association=association).order_by('-start_date')  # Order by start date
    print(years)
    return render(request, 'home/finance/financial_year_list.html', {'years': years})







def request_loan_step1(request, slug):
    # Get the current member's membership based on active association
    member = request.user.memberships.filter(active_association=True).first()
    if not member:
        # Handle the case where there is no active association for the user
        return HttpResponse("No active association found for the user.", status=400)

    # Get the account settings based on the provided slug
    account = get_object_or_404(AccountSettings, slug=slug)

    # Get the last transaction for the member in the given account
    last_transaction = Transaction.objects.filter(member=member, account=account).order_by('-date').first()
    # Set member_balance based on the last transaction's balance_after_transaction, or 0.00 if no transaction exists
    member_balance = last_transaction.balance_after_transaction if last_transaction else Decimal('0.00')

    # Calculate minimum loan amount and maximum eligible loan amount
    min_loan_amount = account.minimum_loan_amount if account.minimum_loan_amount else Decimal('0.00')
    max_loan_amount = (account.eligible_loan_percentage / Decimal(100)) * member_balance

    if request.method == 'POST':
        form = LoanRequestForm(request.POST, account_settings=account, member_balance=member_balance)
        if form.is_valid():
            loan_request = form.save(commit=False)
            loan_request.member = member
            loan_request.account = account
            loan_request.save()
            return redirect('request_loan_step2', loan_request_id=loan_request.id)
    else:
        form = LoanRequestForm(account_settings=account, member_balance=member_balance)

    context = {
        'form': form,
        'member_balance': member_balance,
        'min_loan_amount': min_loan_amount,  # Pass minimum loan amount to the template
        'max_loan_amount': max_loan_amount,  # Pass maximum loan amount to the template
        'eligible_loan_percentage': account.eligible_loan_percentage,
    }
    return render(request, 'home/finance/request_loan_step1.html', context)









def request_loan_step2(request, loan_request_id):
    loan_request = get_object_or_404(LoanRequest, id=loan_request_id)
    account_settings = loan_request.account

    # If no guarantor is required, skip to the next step
    if not account_settings.require_guarantor:
        return redirect('request_loan_step3', loan_request_id=loan_request.id)

    # Get eligible members who are not the loan requester
    eligible_members = Membership.objects.filter(
        member_associations=account_settings.association,
        active_association=True,
    ).exclude(id=loan_request.member.id)

    # Exclude members with active loans if required by settings
    if account_settings.guarantor_must_not_have_loan:
        eligible_members = eligible_members.filter(has_active_loan=False)

    # Get balances for eligible guarantors from their last transaction
    guarantors_balances = {}
    for member in eligible_members:
        last_transaction = Transaction.objects.filter(member=member).order_by('-date').first()
        guarantors_balances[member.id] = last_transaction.balance_after_transaction if last_transaction else Decimal(0.00)

    if request.method == 'POST':
        selected_guarantor_ids = request.POST.getlist('guarantors')
        total_guarantor_balance = Decimal(0.00)

        # Clear any previous guarantors from the Guarantor model for this loan request
        Guarantor.objects.filter(loan_request=loan_request).delete()

        # Create guarantor records in the Guarantor model
        for guarantor_id in selected_guarantor_ids:
            guarantor = get_object_or_404(Membership, id=guarantor_id)
            guarantor_balance = guarantors_balances.get(guarantor.id, Decimal(0.00))
            total_guarantor_balance += guarantor_balance

            # Save the guarantor request with status "Pending"
            Guarantor.objects.create(
                loan_request=loan_request,
                guarantor=guarantor,
                status='Pending'
            )

            # Create a notification for each guarantor
            Notifications.objects.create(
                added_by=loan_request.member,  # The member performing the action
                
                message=f"{loan_request.member.first_name} {loan_request.member.last_name}has requested you to guarantee a loan of {loan_request.amount}.",  # Informing them of the loan request
                is_group_notification=True,  # This notification is for all group members
            )

        # Check if the total guarantor balance covers the loan if required
        if account_settings.guarantor_balance_must_cover_loan and total_guarantor_balance < loan_request.amount:
            # Delete the created guarantor requests since the condition is not met
            Guarantor.objects.filter(loan_request=loan_request).delete()

            return render(request, 'home/finance/request_loan_step2.html', {
                'loan_request': loan_request,
                'eligible_members': eligible_members,
                'guarantors_balances': guarantors_balances,
                'error': 'The combined balance of guarantors must cover the loan amount.'
            })

        # Redirect to the next step or loan requests page
        return redirect('loanrequests', slug=account_settings.slug)

    # Context for the template
    context = {
        'loan_request': loan_request,
        'eligible_members': eligible_members,
        'guarantors_balances': guarantors_balances,
    }
    return render(request, 'home/finance/request_loan_step2.html', context)

def request_loan_step3(request, loan_request_id):
    loan_request = get_object_or_404(LoanRequest, id=loan_request_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            loan_request.status = 'Approved'
            loan_request.approval_date = timezone.now()
            loan_request.save()
        elif action == 'reject':
            loan_request.status = 'Rejected'
            loan_request.save()
        return redirect('loan_requests')  # Redirect to the loan requests list

    context = {
        'loan_request': loan_request,
    }
    return render(request, 'loan/request_loan_step3.html', context)




def list_loan_requests(request, slug):
    account = get_object_or_404(AccountSettings, slug=slug)
    
    # Get the active association for the current member
    active_membership = Membership.objects.filter(
        member=request.user, 
        active_association=True
    ).first()
    
    if not active_membership:
        # Handle the case where there is no active association
        return render(request, 'loan_requests_list.html', {
            'loan_requests': [],
            'error': 'No active association found for the current member.',
        })
    
    # Filter loan requests by active association and account ID
    loan_requests = LoanRequest.objects.filter(
        account=account
        
    ).select_related('member', 'account').prefetch_related('guarantor_requests').order_by('-id')

    # Render the loan requests list template
    return render(request, 'home/finance/loan_request.html', {
        'loan_requests': loan_requests,
        'account': account,
        'active_association': active_membership.member_associations,
    })




def guarantor_requests_view(request):
    # Assuming you have a way to get the current member
    current_member = Membership.objects.filter(
        member=request.user, 
        active_association=True
    ).first()  # Update this based on how you access the member

    if not current_member:
        # Handle the case where the member is not found
        return render(request, 'home/finance/gaurantor_requests.html', {
            'guarantor_requests': [],
            'error': 'No active membership found for the current user.'
        })

    # Fetch guarantor requests where the current member is a guarantor
    guarantor_requests = Guarantor.objects.filter(guarantor=current_member)

    context = {
        'guarantor_requests': guarantor_requests,
    }
    return render(request, 'home/finance/gaurantor_requests.html', context)




def accept_guarantor_request(request, guarantor_id):
    if request.method == "POST":
        # Fetch the guarantor request
        guarantor_request = get_object_or_404(Guarantor, id=guarantor_id)

        # Update the status to "Accepted"
        guarantor_request.accept()  # Assuming you have a method in the Guarantor model to handle this

        messages.success(request, f"Guarantor request for {guarantor_request.loan_request.member} has been accepted.")
        
        # Redirect back to the guarantor requests view
        return redirect('guarantor_requests_view')  # Adjust the URL name as necessary




def reject_guarantor_request(request, guarantor_id):
    if request.method == "POST":
        # Fetch the guarantor request
        guarantor_request = get_object_or_404(Guarantor, id=guarantor_id)

        # Update the status to "Rejected"
        guarantor_request.reject()  # Assuming you have a method in the Guarantor model to handle this

        messages.error(request, f"Guarantor request for {guarantor_request.loan_request.member} has been rejected.")
        
        # Redirect back to the guarantor requests view
        return redirect('guarantor_requests_view')  # Adjust the URL name as necessary
        
        
 



def approve_loan_request(request, loan_request_id):
    # Ensure only the treasurer can perform this action

    # Fetch the loan request
    loan_request = get_object_or_404(LoanRequest, id=loan_request_id)

    # Get the associated account settings
    account_settings = loan_request.account

    # Check if all guarantors have accepted
    if not loan_request.all_guarantors_accepted():
        messages.error(request, "Not all guarantors have accepted the request.")
        return redirect('loanrequests', slug=account_settings.slug)

    # Update the loan status to "Approved"
    loan_request.status = 'Approved'
    loan_request.approval_date = timezone.now()
    loan_request.save()

    # Add a success message
    messages.success(request, f"The loan for {loan_request.member} has been approved.")
    member = Membership.objects.get(member=request.user, active_association=True)
    # Create a notification for the entire association
    Notifications.objects.create(
        added_by=member,  # Assuming the request user is linked to the Membership model
        
        message=f"A loan has been approved for {loan_request.member}.",
        is_group_notification=True  # Indicates that the notification is for the whole association
    )

    # Redirect with a success message
    return redirect('loanrequests', slug=account_settings.slug)
