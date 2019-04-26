# This file contains html forms defined
# programatically by python classes

# imported in views.py

from django import forms

### AUTH forms ###

# for login.html
class LoginForm(forms.Form):
    userName = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'User Name',
        'name': 'userName',
        'id': 'userName',
        'class': 'floating'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Password',
        'name': 'userName',
        'id': 'userName',
        'class': 'floating'
    }))
