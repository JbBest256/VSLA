from django import forms
from .models import FinancialYear, AccountSettings, Transaction,LoanRequest
from membership.models import Membership
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()
class FinancialYearForm(forms.ModelForm):
    class Meta:
        model = FinancialYear
        fields = ['year', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date >= end_date:
            raise forms.ValidationError("The start date must be before the end date.")

        return cleaned_data


class AccountSettingsForm(forms.ModelForm):
    class Meta:
        model = AccountSettings
        fields = [
            'name', 'share_price',
            'minimum_deposit', 'maximum_deposit', 'interest_rate',
            'allow_loans', 'require_guarantor', 'guarantor_must_not_have_loan', 
            'guarantor_balance_must_cover_loan', 'minimum_loan_amount',
            'maximum_loan_amount', 'eligible_loan_percentage',
            'deposit_frequency_per_week', 'deposit_day_of_week'
        ]

    def clean(self):
        cleaned_data = super().clean()
        minimum_deposit = cleaned_data.get('minimum_deposit')
        maximum_deposit = cleaned_data.get('maximum_deposit')
        minimum_loan_amount = cleaned_data.get('minimum_loan_amount')
        maximum_loan_amount = cleaned_data.get('maximum_loan_amount')

        # Validate that the minimum deposit is less than or equal to the maximum deposit
        if minimum_deposit and maximum_deposit and minimum_deposit > maximum_deposit:
            raise forms.ValidationError("Minimum deposit cannot be greater than maximum deposit.")

        # Validate that the minimum loan amount is less than or equal to the maximum loan amount
        if minimum_loan_amount and maximum_loan_amount and minimum_loan_amount > maximum_loan_amount:
            raise forms.ValidationError("Minimum loan amount cannot be greater than maximum loan amount.")

        return cleaned_data


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['member', 'amount', 'transaction_type', 'transaction_mode', 'transaction_id','description']

    def __init__(self, *args, **kwargs):
        active_association = kwargs.pop('active_association', None)
        super().__init__(*args, **kwargs)

        if active_association:
            # Filter members based on the active association and active membership
            self.fields['member'].queryset = Membership.objects.filter(
                member_associations=active_association,
                active_association=True
            )
        else:
            # Clear the queryset if there's no active association
            self.fields['member'].queryset = Membership.objects.none()
            
            
            
class LoanRequestForm(forms.ModelForm):
    class Meta:
        model = LoanRequest
        fields = ['amount', 'description']

    def __init__(self, *args, **kwargs):
        # Extracting account settings and member balance from kwargs
        self.account_settings = kwargs.pop('account_settings', None)
        self.member_balance = kwargs.pop('member_balance', Decimal(0.00))
        super().__init__(*args, **kwargs)

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        
        # Ensure the amount is greater than zero
        if amount <= Decimal(0.00):
            raise forms.ValidationError("The loan amount must be greater than zero.")
        
        # Validate against account settings
        max_loan_amount = (self.account_settings.eligible_loan_percentage / Decimal(100)) * self.member_balance
        min_loan_amount = self.account_settings.minimum_loan_amount  # Use minimum_loan_amount from the model

        # Ensure the loan amount is within the allowed range
        if not (min_loan_amount <= amount <= max_loan_amount):
            raise forms.ValidationError(f"The loan amount must be between {min_loan_amount} and {max_loan_amount}.")
        
        return amount

    def clean(self):
        # Additional cleaning can be done here if necessary
        cleaned_data = super().clean()
        return cleaned_data