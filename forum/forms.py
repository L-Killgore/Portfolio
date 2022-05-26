from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.forms.widgets import FileInput
from .models import Post
from main.models import Profile

User = get_user_model()

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = '__all__'
        exclude = ['banner', 'user', 'post_count']
        widgets = {
            'image': FileInput()
        }

class LoginForm(forms.Form):
    username = forms.CharField(max_length=64, widget=forms.TextInput(attrs={'autofocus': True}))
    password = forms.CharField(max_length=64, widget=forms.PasswordInput())

class NewTopicForm(forms.ModelForm):
    new_topic = forms.CharField(max_length=64, label='', widget=forms.TextInput(attrs={
        'autofocus': True,
        'placeholder': 'New Topic',
        }))

    class Meta:
        model = Post
        fields = ['new_topic', 'content', 'image_upload']
        labels = {
            'content': ''
        }
        widgets = {
            'content': forms.Textarea(attrs={'placeholder': 'New Post', 'rows': 3})
        }

class NewPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'image_upload']
        labels = {
            'content': ''
        }
        widgets = {
            'content': forms.Textarea(attrs={'placeholder': 'New Post', 'rows': 3})
        }