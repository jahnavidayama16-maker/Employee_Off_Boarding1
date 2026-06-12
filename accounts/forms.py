from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, Department

class EmployeeCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False, help_text="Leave blank to auto-generate password as 'employee123'.")
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=False, empty_label="Select Department")

    class Meta:
        model = CustomUser
        fields = ('email', 'full_name', 'department')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'Employee'
        # Default password if none provided
        raw_password = self.cleaned_data.get('password')
        if not raw_password:
            raw_password = 'employee123'
        user.set_password(raw_password)
        if commit:
            user.save()
        return user


class EmployeeEditForm(forms.ModelForm):
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=False, empty_label="Select Department")

    class Meta:
        model = CustomUser
        fields = ('email', 'full_name', 'department')
