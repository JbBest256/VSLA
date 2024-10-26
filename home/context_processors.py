from django.db.models import Q
from membership.models import Membership
from finance.models import AccountSettings, FinancialYear
from home.models import Notifications

def active_user(request):
    active_association = None  # To hold active association if found
    accounts = []
    unread_notifications_count = 0

    if request.user.is_authenticated:
        user = request.user
        # Get active association for the authenticated user
        try:
            active_association = Membership.objects.get(member=user, active_association=True).member_associations
        except Membership.DoesNotExist:
            active_association = None
        
        # Get the active financial year for the active association
        if active_association:
            try:
                active_financial_year = FinancialYear.objects.get(association=active_association, active_status=True)
            except FinancialYear.DoesNotExist:
                active_financial_year = None

            # If both active association and financial year are found, fetch the related accounts
            if active_financial_year:
                accounts = AccountSettings.objects.filter(
                    association=active_association,
                    financial_year=active_financial_year
                )
        
        # Fetch unread notifications for the user (both individual and group notifications)
        # Fetch count of unread notifications for the user (both individual and group notifications)
        try:
            member = Membership.objects.get(member=user, active_association=True)
            unread_notifications_count = Notifications.objects.filter(
                Q(recipient=member) | Q(is_group_notification=True, added_by__member_associations=active_association),
                is_read=False
            ).count()  # Use .count() to get the number of unread notifications
        except Membership.DoesNotExist:
            unread_notifications_count = 0  # If no membership found, set count to 0


    return {
        'active_association': active_association,
        'accounts': accounts,  # Pass the fetched accounts to the context
        'unread_notifications_count': unread_notifications_count,  # Pass unread notifications to the context
    }
