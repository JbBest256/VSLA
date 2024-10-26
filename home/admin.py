from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import UserAdminCreationForm,UserAdminChangeForm
from association.models import Association, GeneralPermissions, AssociationRoles, RolePermission
from membership.models import Membership, Staff
from finance.models import FinancialYear,AccountSettings,Transaction
User = get_user_model()
# Register your models here.



admin.site.register(Transaction)
admin.site.register(Association)
admin.site.register(GeneralPermissions)
admin.site.register(AssociationRoles)
admin.site.register(RolePermission)
admin.site.register(Membership)
admin.site.register(Staff)
admin.site.register(FinancialYear)
admin.site.register(AccountSettings)



class UserAdmin(BaseUserAdmin):
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm
   
    list_display = ['phone_number','user_name','admin','is_active','staff']
    list_filter = ['admin','is_active','staff']
    fieldsets = ( 
        (None,{'fields':('phone_number','user_name','password')}),
        ('Personal info',{'fields':()}),
        ('Permissions',{'fields':('admin','staff')}),
    
    )
    
    add_fieldsets = (
        (None,{
            'classes':('wide',),
            'fields':('phone_number','user_name','password','password_2')}
        ),
    )

    search_fields = ['phone_number']
    ordering = ['phone_number']
    filter_horizontal = ()
admin.site.register(User,UserAdmin) 
