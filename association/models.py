from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Association(models.Model):
    ACTIVE_STATUS_CHOICES = [
        ('On', 'On'),
        ('Off', 'Off'),
    ]

    active_status = models.CharField(max_length=10, choices=ACTIVE_STATUS_CHOICES, default='Off')
    founder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='founder')
    
    profile_image = models.ImageField(upload_to='media/', null=True, blank=True)
    cover_image = models.ImageField(upload_to='media/', null=True, blank=True)
    
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    currency = models.CharField(max_length=255)
    slogan = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, null=True, blank=True)  # Use EmailField for email
    about = models.TextField(null=True, blank=True)
    seo = models.TextField(null=True, blank=True)
    date_created = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name

class GeneralPermissions(models.Model):
    identity = models.IntegerField(unique=True) 
    permission_name = models.CharField(max_length=255)
    date_created = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.permission_name
        
class AssociationRoles(models.Model):
    role_association = models.ForeignKey(Association, on_delete=models.CASCADE, related_name='roles')
    role_name = models.CharField(max_length=255)    
    date_created = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.role_name

class RolePermission(models.Model):
    role = models.ForeignKey(AssociationRoles, on_delete=models.CASCADE, related_name='permissions')
    permission = models.ForeignKey(GeneralPermissions, null=True, blank=True, on_delete=models.CASCADE, related_name='role_permissions')
    date_created = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.role} - {self.permission}"
