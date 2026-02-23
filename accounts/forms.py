from django import forms
from django.contrib.auth.models import User
from .models import Profile
import re
class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput,min_length=8)
    confirm_password=forms.CharField(widget=forms.PasswordInput,label="confirm Password")
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES)

    class Meta:
        model = User
        fields = ['username','email','password']


    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()

        if len(username) < 3:
            raise forms.ValidationError("Username must be at least 3 characters long.")

        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("This username is already taken.")

        return username

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()

        if not email:
            raise forms.ValidationError("Email is required.")

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")

        return email

    def clean_password(self):
        password = self.cleaned_data.get('password', '')

        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError("Password must contain at least one uppercase letter.")

        if not re.search(r'[a-z]', password):
            raise forms.ValidationError("Password must contain at least one lowercase letter.")

        if not re.search(r'\d', password):
            raise forms.ValidationError("Password must contain at least one digit.")

        if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', password):
            raise forms.ValidationError("Password must contain at least one special character.")

        return password

    def clean_role(self):
        role = self.cleaned_data.get('role')
        valid_roles = [choice[0] for choice in Profile.ROLE_CHOICES]

        if role not in valid_roles:
            raise forms.ValidationError("Invalid role selected.")

        return role

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        username = cleaned_data.get('username', '')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

        if password and username and username.lower() in password.lower():
            self.add_error('password', "Password must not contain your username.")

        return cleaned_data