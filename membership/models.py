from django.db import models
from django.contrib.auth import get_user_model
from association.models import AssociationRoles, Association

User = get_user_model()

class Membership(models.Model):
    MEMBERSHIP_CHOICES = [
        ('Member', 'Member'),
        ('Official', 'Official'),
        ('Inactive', 'Inactive'),
    ]
    profile_image = models.ImageField(upload_to='media/', null=True, blank=True)
    national_id_or_passport = models.ImageField(upload_to='media/', null=True, blank=True)
    membership_status = models.CharField(max_length=10, choices=MEMBERSHIP_CHOICES, default='Member')
    member_associations = models.ForeignKey(Association, on_delete=models.CASCADE, blank=True, null=True)  # A member can belong to multiple associations
    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memberships')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    active_association = models.BooleanField(default=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    has_active_loan= models.BooleanField(default=False)
    class Meta:
        unique_together = ('member', 'member_associations')


    def __str__(self):
        return f"{self.first_name} {self.last_name} "


class Staff(models.Model):
    assigned_staff = models.ForeignKey(Membership, on_delete=models.CASCADE, related_name='staff_assignments')  
    staff_role = models.ForeignKey(AssociationRoles, on_delete=models.CASCADE, related_name='staff_members', null=True, blank=True)    
    date_created = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.assigned_staff.first_name} {self.assigned_staff.last_name} - {self.staff_role.role_name if self.staff_role else 'No Role'}"
