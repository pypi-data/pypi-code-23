from django import forms
from django.contrib.auth import get_user_model


_OctoUser = get_user_model()


class UserCreationForm(forms.ModelForm):

    error_messages = {
        'duplicate_email': "Пользователь с таким email уже существует.",
        'password_mismatch': "Пароли не сопадают.",
    }
    email = forms.EmailField(label="Email",)
    password1 = forms.CharField(label="Пароль",
        widget=forms.PasswordInput)
    password2 = forms.CharField(label="Подтверждение пароль",
        widget=forms.PasswordInput,
        help_text="Введите пароль еще раз, для подтверждения.")

    class Meta:
        model = _OctoUser
        fields = ("email",)

    def clean_username(self):
        email = self.cleaned_data["email"]
        try:
            _OctoUser.objects.get(email=email)
        except _OctoUser.DoesNotExist:
            return email
        raise forms.ValidationError(self.error_messages['duplicate_email'])

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'])
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
