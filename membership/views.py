
from django.shortcuts import render, redirect, get_object_or_404
from association.forms import MembershipForm
from .models import Membership, Staff
from association.models import Association,AssociationRoles
from association.forms import AssignStaffForm
from django.contrib.auth import get_user_model
User = get_user_model()  
# Create your views here.
def MembersView(request):
    user = request.user
    member = Membership.objects.get(active_association = True, member = user)
    pk = member.member_associations.id
    members = Membership.objects.filter(member_associations__id = pk)
    
    return render(request, 'home/membership/allmembers.html', {
        'members': members
    })
    
    
    
def LeadersView(request):
    user = request.user
    active_association = Membership.objects.get(member=request.user, active_association=True).member_associations
    
    staffs = Staff.objects.filter(staff_role__role_association = active_association)
    
    return render(request, 'home/membership/allstaff.html', {
        'staffs': staffs
    })
        
  



def AddMemberView(request):
    user = request.user
    member = Membership.objects.get(active_association=True, member=user)
    association = get_object_or_404(Association, id=member.member_associations.id)

    if request.method == 'POST':
        membership_form = MembershipForm(request.POST, request.FILES)

        if membership_form.is_valid():
            phone_number = membership_form.cleaned_data['phone_number']
            print(phone_number)
            users = User.objects.all()
            print(users)
            # Check if a user with the given phone number exists in the system
            try:
                existing_user = User.objects.get(phone_number=phone_number)
            except User.DoesNotExist:
                # Throw an error if the user does not exist in the system
                return render(request, 'home/membership/addmember.html', {
                    'membership_form': membership_form,
                    'association': association,
                    'error': 'No user is registered with the provided phone number.'
                })

            # Check if the user is already a member of the association
            if Membership.objects.filter(member=existing_user, member_associations=association).exists():
                return render(request, 'home/membership/addmember.html', {
                    'membership_form': membership_form,
                    'association': association,
                    'error': 'This user is already a member of the association.'
                })

            # Add the existing user to the association
            membership = membership_form.save(commit=False)
            membership.member = existing_user
            membership.member_associations = association
            membership.active_association = True
            membership.save()

            return redirect('members')  # Replace 'members_url' with the actual URL name for the members page

        else:
            # If form is not valid, show form errors
            print("Membership Form Errors:", membership_form.errors)

    else:
        membership_form = MembershipForm()

    return render(request, 'home/membership/addmember.html', {
        'membership_form': membership_form,
        'association': association
    })

# Create your views here.
def ConfirmRemoveMemberView(request):
   
    
    return render(request, 'home/home/home.html')


def AssignStaff(request, pk):
    role = get_object_or_404(AssociationRoles, id=pk)
    form = AssignStaffForm()
    if request.method == 'POST':
        form = AssignStaffForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data.get('phone_number')
            User = get_user_model()
            try:
                staff_ = User.objects.get(phone_number=phone_number)
                # Get active association for the authenticated user
                
                try:
                    active_association = Membership.objects.get(member=request.user, active_association=True).member_associations
                    member = Membership.objects.get(member_associations = active_association, member = staff_)
                    _staff = Staff.objects.create(assigned_staff = member, staff_role = role)
                    # Additional logic to assign the staff to the role can go here
                    return redirect('roles') 
                except Membership.DoesNotExist:
                    active_association = None
                    form.add_error('phone_number', 'User is not a member of this association.')
                    return render(request, 'home/roles/assignstaff.html', {
            'form': form,
          
            'role': role,
        })
                    # Additional logic to assign the staff to the role can go here
                    return redirect('roles') 
            except User.DoesNotExist:
                form.add_error('phone_number', 'No Association Member found with this phone number.')
                return render(request, 'home/roles/assignstaff.html', {
        'form': form,
      
        'role': role,
    })
    else:
        form = AssignStaffForm()

    return render(request, 'home/roles/assignstaff.html', {
        'form': form,
      
        'role': role,
    })
    