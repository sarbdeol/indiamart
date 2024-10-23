from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import CategoryKeyword, RejectedKeyword
# User Registration Form
class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

# Login Form
class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username or Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))



from .models import IndiaMartAccount

class IndiaMartAccountForm(forms.ModelForm):
    class Meta:
        model = IndiaMartAccount
        fields = ['indiamart_username', 'indiamart_password']
        widgets = {
            'indiamart_password': forms.PasswordInput(),  # Mask password input
        }
        labels = {
            'indiamart_username': 'IndiaMart Username',
            'indiamart_password': 'IndiaMart Password',
        }


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = IndiaMartAccount
        fields = ['indiamart_username', 'indiamart_password']
        widgets = {
            'indiamart_password': forms.PasswordInput(),
        }
        labels = {
            'indiamart_username': 'IndiaMart Username',
            'indiamart_password': 'IndiaMart Password',
        }


class CategoryKeywordForm(forms.ModelForm):
    class Meta:
        model = CategoryKeyword
        fields = ['keyword']

class RejectedKeywordForm(forms.ModelForm):
    class Meta:
        model = RejectedKeyword
        fields = ['keyword']


class QuantityForm(forms.ModelForm):
    class Meta:
        model = IndiaMartAccount
        fields = ['quantity']