from django.db import models
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.utils.text import slugify
import uuid
from association.models import AssociationRoles, Association
from membership.models import Membership
User = get_user_model()

class FinancialYear(models.Model):
    association = models.ForeignKey(Association, on_delete=models.CASCADE)
    year = models.CharField(max_length=9)  # e.g., "2024-2025"
    start_date = models.DateField()
    end_date = models.DateField()
    active_status = models.BooleanField(default=False)

    class Meta:
        unique_together = ('association', 'year')  # Ensures uniqueness within the association

    def __str__(self):
        return f"{self.year} ({self.association.name})"

class AccountSettings(models.Model):
    association = models.ForeignKey(Association, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=100)  # e.g., "Savings", "Loan", "Fine"
    financial_year = models.ForeignKey('FinancialYear', on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, max_length=150, blank=True, null=True)  # Slug field for dynamic URLs
    share_price = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_deposit = models.DecimalField(max_digits=10, decimal_places=2)
    maximum_deposit = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_loan_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    maximum_loan_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="Interest rate in percentage")
    eligible_loan_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text=" In percentage")
    allow_loans = models.BooleanField(default=False)
    require_guarantor = models.BooleanField(default=False)  # Requires at least one guarantor

    # New fields for guarantor conditions
    guarantor_must_not_have_loan = models.BooleanField(default=False, help_text="Guarantor must not have a loan.")
    guarantor_balance_must_cover_loan = models.BooleanField(default=False, help_text="Combined balance of guarantors must cover the loan amount.")

    deposit_frequency_per_week = models.PositiveIntegerField(default=1, help_text="Number of times deposits can be made per week")
    deposit_day_of_week = models.CharField(max_length=9, blank=True, null=True, choices=[
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday')
    ], help_text="Specify the day of the week for deposits if applicable")

    class Meta:
        unique_together = ('association', 'name', 'financial_year')  # Ensures uniqueness within the association and financial year

    def save(self, *args, **kwargs):
        if not self.slug:
            # Create a slug from the name and a UUID to ensure uniqueness
            self.slug = slugify(self.name) + '-' + str(uuid.uuid4())[:8]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} Settings for {self.financial_year.year} ({self.association.name})"



class Transaction(models.Model):
    TRANSACTION_MODES = [
        ('Cash', 'Cash'), 
        ('Mobile Money', 'Mobile Money'), 
        ('Bank', 'Bank'),
        
        
    ]
    TRANSACTION_TYPES = [
        ('Deposit', 'Deposit'), 
        ('Withdrawal', 'Withdrawal'), 
        ('Loan', 'Loan'),
        ('Expense', 'Expense'), 
        ('Dividend', 'Dividend'),  # Added type for dividends
        
    ]

    member = models.ForeignKey(Membership, on_delete=models.CASCADE, blank=True, null=True,)
    account = models.ForeignKey(AccountSettings, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    transaction_mode = models.CharField(max_length=20, default='Cash',choices=TRANSACTION_MODES)
    shares = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Number of shares involved in the transaction, if applicable")
    balance_after_transaction = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, help_text="Member's balance after this transaction")
    account_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0, help_text="Member's balance after this transaction")
    description = models.TextField(blank=True, null=True, help_text="Optional description or notes about the transaction")
    transaction_id = models.CharField(max_length=50, blank=True, null=True, help_text="Unique reference for tracking the transaction")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} of {self.amount} by {self.member.first_name} on {self.date}"

    class Meta:
        ordering = ['-date']
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"
      

            
class LoanRequest(models.Model):
    LOAN_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    member = models.ForeignKey(Membership, on_delete=models.CASCADE, related_name='loan_requests')
    account = models.ForeignKey(AccountSettings, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=LOAN_STATUS_CHOICES, default='Pending')
    request_date = models.DateTimeField(auto_now_add=True)
    approval_date = models.DateTimeField(blank=True, null=True)
    
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Loan Request: {self.member} - {self.amount} ({self.status})"

    @property
    def is_approved(self):
        return self.status == 'Approved'

    @property
    def is_rejected(self):
        return self.status == 'Rejected'

    def eligible_for_guarantors(self):
        return self.account.require_guarantor

    def all_guarantors_accepted(self):
        # Check if all guarantors for this loan request have accepted
        return not self.guarantor_requests.filter(status='Pending').exists()          


class Guarantor(models.Model):
    loan_request = models.ForeignKey(LoanRequest, on_delete=models.CASCADE, related_name='guarantor_requests')
    guarantor = models.ForeignKey(Membership, on_delete=models.CASCADE, related_name='guarantor_for_loans')
    status_choices = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected')
    ]
    status = models.CharField(max_length=10, choices=status_choices, default='Pending')
    requested_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True, help_text="Optional notes from the guarantor")

    def accept(self):
        self.status = 'Accepted'
        self.responded_at = timezone.now()
        self.save()

    def reject(self):
        self.status = 'Rejected'
        self.responded_at = timezone.now()
        self.save()

    def __str__(self):
        return f"Guarantor: {self.guarantor} for Loan Request: {self.loan_request} - {self.status}"


class LoanRepayment(models.Model):
    loan_request = models.ForeignKey(LoanRequest, on_delete=models.CASCADE, related_name='repayments')
    member = models.ForeignKey(Membership, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    repayment_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-repayment_date']
        verbose_name = "Loan Repayment"
        verbose_name_plural = "Loan Repayments"

    def __str__(self):
        return f"{self.amount_paid} repayment for {self.loan_request} by {self.member} on {self.repayment_date}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update the loan request status based on total repayments
        total_repayments = sum(repayment.amount_paid for repayment in self.loan_request.repayments.all())
        
        # Check if the total repayments cover the loan amount
        if total_repayments >= self.loan_request.amount:
            self.loan_request.status = 'Paid'
        else:
            self.loan_request.status = 'Active'  # Loan is still being repaid
        self.loan_request.save()
