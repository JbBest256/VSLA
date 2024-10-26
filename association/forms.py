from django import forms
from phonenumber_field.formfields import PhoneNumberField
from .models import Association,AssociationRoles, RolePermission, GeneralPermissions
from membership.models import Membership

class AssociationForm(forms.ModelForm):
    class Meta:
        model = Association
        fields = ['name', 'address', 'country', 'currency', 'slogan', 'phone', 'email', 'about', 'seo', 'profile_image', 'cover_image']

class MembershipForm(forms.ModelForm):
    class Meta:
        model = Membership
        fields = ['profile_image','national_id_or_passport','first_name', 'last_name', 'email', 'phone_number']




class RoleForm(forms.ModelForm):
    class Meta:
        model = AssociationRoles
        fields = ['role_name']
        
class AssignStaffForm(forms.Form):
    phone_number = PhoneNumberField()  
        

    
