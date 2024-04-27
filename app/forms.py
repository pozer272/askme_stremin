from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from app.models import myUser
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput, max_length=150)

    # username = username.strip()  # очистка пробелов

    def clean_username(self):
        username = self.cleaned_data["username"]
        if not User.objects.filter(username=username).exists():
            raise ValidationError("There is no such user")
        return username

    # def clean_password(self):
    #     username = self.cleaned_data["username"]
    #     password = self.cleaned_data["password"]

    #     if username and password:
    #         user = authenticate(username=username, password=password)
    #         if user is None:
    #             raise ValidationError("Invalid password")

    #     return password

    def clean(self):
        super().clean()
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        user = authenticate(username=username, password=password)
        if user is None:
            raise ValidationError("Invalid username or password")
        return self.cleaned_data


class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    avatar = forms.ImageField()

    # def clean_confirm_password(self):
    #     password = self.cleaned_data.get("password")
    #     confirm_password = self.cleaned_data.get("confirm_password")
    #     if password != confirm_password:
    #         raise ValidationError("Passwords don't match")
    #     return confirm_password

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "password"]

    # def save(self, commit=True):
    #     django_user = (
    #         self.instance.django_user
    #         if self.instance
    #         else User.objects.create_user(username=self.cleaned_data["username"])
    #     )
    #     django_user.set_password(self.cleaned_data["password"])
    #     django_user.save()
    #     user = super().save(commit=False)
    #     user.django_user = django_user
    #     if commit:
    #         user.save()
    #     return user
