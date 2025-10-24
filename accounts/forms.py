from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=True)
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, initial='customer')


    class Meta:
        model = User
        fields = ['username', 'email', 'phone','address', 'password1', 'password2', 'role','profile_image']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        } 
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = self.cleaned_data['role']  # explicitly set role
        if commit:
            user.save()
        return user