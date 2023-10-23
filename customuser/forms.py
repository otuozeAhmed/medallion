# customuser/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'full_name', 'department', 'unit', 'staff_id', 'password1', 'password2')

     # Use the PasswordInput widget to render the password input
    widgets = {
        'password1': forms.PasswordInput(attrs={'minlength': '4'}),
        'password2': forms.PasswordInput(attrs={'minlength': '4'}),
    }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        allowed_domains = ["nlng.com", "raisbny.com"]
        domain = email.split('@')[1] if '@' in email else None
        if domain not in allowed_domains:
            raise forms.ValidationError('Only NLNG and RAISBNY email addresses are allowed.')
        return email
    
    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name')
        # Add custom validation logic for full_name
        if len(full_name) < 2:
            raise forms.ValidationError('Full name must be at least 2 characters long.')
        return full_name
    
    def clean_staff_id(self):
        staff_id = self.cleaned_data.get('staff_id')
        if CustomUser.objects.filter(staff_id=staff_id).exists():
            raise forms.ValidationError('This staff ID is already in use.')
        return staff_id
    
    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if len(password1) < 4:
            raise forms.ValidationError("Password must be at least 4 characters long.")
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        return password2
    
    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        if self.instance:
            # Populate the form with the user's previously entered data
            self.fields['email'].initial = self.instance.email
            self.fields['full_name'].initial = self.instance.full_name
            self.fields['department'].initial = self.instance.department
            self.fields['unit'].initial = self.instance.unit
            self.fields['staff_id'].initial = self.instance.staff_id
