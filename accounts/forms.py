from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'autocomplete': 'email'}),
    )
    phone = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={'autocomplete': 'tel'}),
    )
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, initial='customer')

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'address', 'password1', 'password2', 'role', 'profile_image']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 2}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip().replace(' ', '')
        if not phone.isdigit() or not (10 <= len(phone) <= 15):
            raise forms.ValidationError('Enter a valid 10–15 digit phone number.')
        return phone

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = self.cleaned_data['role']
        if commit:
            user.save()
        return user