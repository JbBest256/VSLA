from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth import get_user_model



class UserManager(BaseUserManager):
    def create_user(self, phone_number, user_name, password=None):
        """
        Creates and saves a regular user with the given phone number, username, and password.
        """
        if not phone_number:
            raise ValueError('Users must have a phone number')
        user = self.model(phone_number=phone_number, user_name=user_name)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, phone_number, user_name, password):
        """
        Creates and saves a staff user with the given phone number, username, and password.
        """
        user = self.create_user(phone_number, user_name, password=password)
        user.staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, user_name, password):
        """
        Creates and saves a superuser with the given phone number, username, and password.
        """
        user = self.create_user(phone_number, user_name, password=password)
        user.staff = True
        user.admin = True
        user.save(using=self._db)
        return user


class UserAuth(AbstractBaseUser, PermissionsMixin):
    phone_number = PhoneNumberField(unique=True)
    user_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['user_name']

    objects = UserManager()

    def __str__(self):
        return str(self.phone_number)

    def get_full_name(self):
        return self.user_name

    def get_short_name(self):
        return self.user_name

    def has_perm(self, perm, obj=None):
        # Placeholder for custom permission logic
        return True

    def has_module_perms(self, app_label):
        # Placeholder for custom permission logic
        return True

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin
        
User = get_user_model()    
from membership.models import Membership




class Notifications(models.Model):
    
    # Changed from User to Membership to track the member performing the action
    added_by = models.ForeignKey(Membership, on_delete=models.CASCADE, related_name='notifications_added', null=True, blank=True)
    # To track if a notification is for all members or one specific member
    recipient = models.ForeignKey(Membership, on_delete=models.CASCADE, related_name='notifications_received', null=True, blank=True)
    
    message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_group_notification = models.BooleanField(default=False)  # Whether the notification is visible to all group members

    def __str__(self):
        return f"Notification by {self.added_by.first_name} - {self.action_type} on {self.created_at}"

    class Meta:
        ordering = ['-created_at']  # Latest notifications first
