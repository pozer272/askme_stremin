from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from app.models import myUser, Answer, Question, Tag
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput, max_length=150)

    def clean_username(self):
        username = self.cleaned_data.get("username").strip()
        self.cleaned_data["username"] = username
        if not User.objects.filter(username=username).exists():
            raise ValidationError("Invalid username")
        return username

    # def clean_password(self):
    #     password = self.cleaned_data.get("password")
    #     return password

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        if not username or not password:
            raise ValidationError("Username and Password are required.")

        user = authenticate(username=username, password=password)

        if user is None:
            raise ValidationError("Invalid username or password.")

        return cleaned_data


class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    avatar = forms.ImageField()

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "avatar", "password"]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Passwords don't match")

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data["username"],
            password=self.cleaned_data["password"],
        )
        my_user = myUser(django_user=user, avatar=self.cleaned_data["avatar"])
        my_user.save()
        return user


class SettingsForm(forms.ModelForm):
    avatar = forms.ImageField()

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "avatar"]


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ["text"]


class QuestionForm(forms.ModelForm):
    tags = forms.CharField(max_length=255)

    class Meta:
        model = Question
        fields = ["title", "text", "image", "tags"]

    def clean_tags(self):
        tags = self.cleaned_data.get("tags")
        tag_list = tags.split()
        if len(tag_list) > 3:
            raise ValidationError("The maximum number of tags is 3")
        return tags

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.author = self.author

        if commit:
            instance.save()

        tags = self.cleaned_data["tags"].split(" ")
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(name=tag)
            instance.tags.add(tag_obj)

        return instance
