# This file contains html forms defined
# programatically by python classes

# imported in views.py

from django import forms

### AUTH forms ###

# for login.html
class LoginForm(forms.Form):
    userName = forms.CharField(widget=forms.TextInput(attrs={
        'name': 'userName',
        'required': True,
        'value': '',
        'class': 'fInput'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'name': 'pass',
        'required': True,
        'value': '',
        'class': 'fInput'
    }))

# for signup.html
class SignupForm(forms.Form):
        userName = forms.CharField(widget=forms.TextInput(attrs={
            'name': 'userName',
            'required': True,
            'value': '',
            'class': 'fInput'
        }))
        password = forms.CharField(widget=forms.PasswordInput(attrs={
            'name': 'pass',
            'required': True,
            'value': '',
            'class': 'fInput'
        }))
        confirmPassword = forms.CharField(widget=forms.PasswordInput(attrs={
            'name': 'confirm',
            'required': True,
            'value': '',
            'class': 'fInput'
        }))
