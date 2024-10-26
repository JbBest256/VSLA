from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.db import transaction
from django.contrib.auth.decorators import login_required
from .models import Association,  AssociationRoles, RolePermission, GeneralPermissions
from membership.models import Membership, Staff
from django.contrib.auth import get_user_model
from .forms import AssociationForm, MembershipForm,RoleForm,RolePermission # Assuming you have forms for these models
from finance.models import Transaction
from django.db.models import OuterRef, Subquery
User = get_user_model()



@login_required
def active_association(request):
    # Fetch the active membership for the logged-in user
    active_membership = Membership.objects.filter(member=request.user, active_association=True).first()

    # Ensure there is an active membership
    if not active_membership:
        return render(request, 'home/association/associationprofile.html', {
            'active_membership': None,
            'last_transactions': None,
        })

    # Subquery to get the latest transaction date for each account
    latest_transaction_subquery = (
        Transaction.objects
        .filter(account=OuterRef('account'), account__association=active_membership.member_associations)
        .order_by('-date')
        .values('date')[:1]  # Get the latest date
    )

    # Get the last transaction for each account type related to the association
    last_transactions = (
        Transaction.objects
        .filter(date=Subquery(latest_transaction_subquery))
        .filter(account__association=active_membership.member_associations)
    )

    return render(request, 'home/association/associationprofile.html', {
        'active_membership': active_membership,
        'last_transactions': last_transactions,  # Pass the last transactions to the template
    })


@login_required
def association_dashboard(request):
    # Fetch the active membership for the logged-in user
    active_membership = Membership.objects.filter(member=request.user, active_association=True).first()
    return render(request, 'home/association/associationdashboard.html', {
        'active_membership': active_membership,
        'transactions': transactions
    })


#CREATE ASSOCIATIONS
def create_association(request):
    if request.method == 'POST':
        association_form = AssociationForm(request.POST, request.FILES)
        membership_form = MembershipForm(request.POST)

        if association_form.is_valid() and membership_form.is_valid():
            try:
                with transaction.atomic():
                    # Create the association
                    association = association_form.save(commit=False)
                    association.founder = request.user
                    association.save()

                    # Get default permission or handle the error if not found
                    try:
                        permission = GeneralPermissions.objects.get(identity=1)
                    except GeneralPermissions.DoesNotExist:
                        return render(request, 'home/association/create_association.html', {
                            'association_form': association_form,
                            'membership_form': membership_form,
                            'error': 'Default permission not found.'
                        })

                    # Create default role
                    chairman_role = AssociationRoles.objects.create(
                        role_association=association,
                        role_name='Founder'
                    )

                    RolePermission.objects.create(
                        role=chairman_role,
                        permission=permission
                    )

                    # Deactivate any existing active memberships for the user
                    Membership.objects.filter(member=request.user, active_association=True).update(active_association=False)

                    # Check if the user is already a member of this association
                    if Membership.objects.filter(member=request.user, member_associations=association).exists():
                        return render(request, 'home/association/create_association.html', {
                            'association_form': association_form,
                            'membership_form': membership_form,
                            'error': 'You are already a member of this association.'
                        })

                    # Save Membership and create Staff entry
                    membership = membership_form.save(commit=False)
                    membership.member = request.user
                    membership.member_associations = association
                    membership.active_association = True
                    membership.save()

                    # Create Staff entry for the founder with the role
                    Staff.objects.create(
                        assigned_staff=membership,
                        staff_role=chairman_role
                    )

                    return redirect('association_detail')  # Ensure this URL is correct
            except Exception as e:
                # Handle unexpected errors
                print(f"Error creating association: {e}")
                return render(request, 'home/association/create_association.html', {
                    'association_form': association_form,
                    'membership_form': membership_form,
                    'error': 'An error occurred while creating the association.'
                })
        else:
            # Log errors if the forms are not valid
            print("Association Form Errors:", association_form.errors)
            print("Membership Form Errors:", membership_form.errors)
    else:
        association_form = AssociationForm()
        membership_form = MembershipForm()

    return render(request, 'home/association/create_association.html', {
        'association_form': association_form,
        'membership_form': membership_form
    })



def AllRolesView(request):
    roles_permissions = {}

    try:
        # Get the active association for the current user
        active_association = Membership.objects.get(member=request.user, active_association=True).member_associations
        roles = AssociationRoles.objects.filter(role_association=active_association)

        # Fetch permissions for each role
        for role in roles:
            # Get permissions associated with the role
            permissions = RolePermission.objects.filter(role=role).select_related('permission')
            roles_permissions[role] = permissions

    except Membership.DoesNotExist:
        active_association = None

    return render(request, 'home/roles/roles.html', {'roles_permissions': roles_permissions})
    
    

def AddRolesView(request):
    permissions = GeneralPermissions.objects.all()
    
    if request.method == 'POST':
        form = RoleForm(request.POST)
        try:
            # Get the active association for the current user
            active_association = Membership.objects.get(member=request.user, active_association=True).member_associations
            
            if form.is_valid():
                # Save the role without committing yet
                role = form.save(commit=False)
                role.role_association = active_association
                role.save()

                # Save the selected permissions, if any
                permissions = request.POST.getlist('permissions[]')
        
                # Process the permissions list
                for permission in permissions:
                    activity = get_object_or_404(GeneralPermissions, identity=permission)
                    RolePermission.objects.create(role=role, permission=activity) # Replace 'BusinessRolePermissions' with your actual model for role permissions
                    

                return redirect('roles')  # Update to the actual success URL
        except Membership.DoesNotExist:
            active_association = None
            form.add_error(None, "Active association not found for the current user.")
        
    else:
        form = RoleForm()

    return render(request, 'home/roles/newrole.html', {'permissions': permissions, 'form': form})


def SingleRole(request, pk):
    
    role = get_object_or_404(AssociationRoles, id=pk)
    permissions = RolePermission.objects.filter(role=role)
    staffs = Staff.objects.filter(staff_role = role)
    return render(request,'home/roles/singlerole.html', {
        'permissions': permissions,
        'role': role,
        'staffs': staffs,
        
    })




def update_association(request, pk):
    association = get_object_or_404(Association, pk=pk)
    if request.method == 'POST':
        form = AssociationForm(request.POST, request.FILES, instance=association)
        if form.is_valid():
            form.save()
            return redirect('association_detail', pk=association.pk)
    else:
        form = AssociationForm(instance=association)
    return render(request, 'update_association.html', {'form': form})

def delete_association(request, pk):
    association = get_object_or_404(Association, pk=pk)
    if request.method == 'POST':
        association.delete()
        return redirect('association_list')
    return render(request, 'delete_association.html', {'association': association})

def association_detail(request, pk):
    association = get_object_or_404(Association, pk=pk)
    return render(request, 'association_detail.html', {'association': association})

def association_list(request):
    associations = Association.objects.all()
    return render(request, 'association_list.html', {'associations': associations})