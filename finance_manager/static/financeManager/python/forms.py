# This file contains html forms defined
# programatically by python classes

# imported in views.py

from django import forms

### AUTH forms ###

# for login.html
class LoginForm(forms.Form):
    userName = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())
