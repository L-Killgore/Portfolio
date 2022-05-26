from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.forms.widgets import FileInput

from main.models import Profile

User = get_user_model()

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['display_name', 'image', 'banner', 'tagline']
        widgets = {
            'image': FileInput(),
            'banner': FileInput()
        }