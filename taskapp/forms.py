from django import forms

class RegisterForm(forms.Form):
    name = forms.CharField()
    surname = forms.CharField()
    email = forms.EmailField()
    login = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)