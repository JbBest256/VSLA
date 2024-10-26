from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from phonenumber_field.formfields import PhoneNumberField
from django.urls import reverse_lazy
from django.contrib.auth import login,authenticate,logout


User = get_user_model()


class LoginForm(forms.Form):
    phone_number = PhoneNumberField()
    password = forms.CharField(widget=forms.PasswordInput)
   
        
    def clean(self):
        phone_number = self.cleaned_data.get('phone_number')
        password = self.cleaned_data.get('password')
        user = authenticate(username=phone_number,password=password)
        if not user or not user.is_active:
            raise forms.ValidationError('Sorry, that login was invalid. Please try again ')
        return self.cleaned_data    
        
class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget= forms.PasswordInput)
    password_2 = forms.CharField(label = 'Confirm Password',widget= forms.PasswordInput)
    
    class Meta:
        model = User
        fields = ['phone_number','user_name']
        
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        qs = User.objects.filter(phone_number=phone_number)
        if qs.exists():
            raise forms.ValidationError('Phone number already exist')
        return phone_number
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_2 = cleaned_data.get('password_2')
        if password is not None and password != password_2:
            self.add_error('password_2','Your passwords must match')
        return cleaned_data

    def save(self,commit = True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user  
        
class EditUserForm(forms.Form):
    phone_number = PhoneNumberField()
    new_phone_number = PhoneNumberField()
    password_c = forms.CharField(label = 'Current Password',widget= forms.PasswordInput)
    password = forms.CharField(label = 'New Password',widget= forms.PasswordInput)
    password_2 = forms.CharField(label = 'Confirm Password',widget= forms.PasswordInput)
   
   
        
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        qs = User.objects.filter(phone_number=phone_number)
        if qs.exists():
            pass
        else:    
            raise forms.ValidationError('Phone number does not exist')
        return phone_number
        
    def clean_phone_number_password(self):
        phone_number = self.cleaned_data.get('phone_number')
        password = self.cleaned_data.get('password_c')
        qs = User.objects.filter(phone_number=phone_number, password= password)
        if qs.exists():
            pass
        else:    
            raise forms.ValidationError('Phone number and current password does not match')
        return cleaned_data
        
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_2 = cleaned_data.get('password_2')
        if password is not None and password != password_2:
            self.add_error('password_2','Your passwords must match')
        return cleaned_data

     
 
 
class UserAdminCreationForm(forms.ModelForm):
    password = forms.CharField(widget = forms.PasswordInput)
    password_2 = forms.CharField(label='Confirm Password',widget = forms.PasswordInput)
    class Meta:
        model = User
        fields = ['phone_number','user_name']
        
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_2 = cleaned_data.get('password_2')
        if password is not None and password !=password_2:
            self.add_error('password_2','Your passwords must mutch')
        return cleaned_data


    def save(self,commit = True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user   
        
class UserAdminChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()
    
    class Meta:
        model = User
        fields = ['phone_number','user_name','password','is_active','admin','staff']

    def clean_password(self):
        return self.initial['password']
        
        
        
    
        
       