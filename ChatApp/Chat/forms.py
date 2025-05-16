from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

class ChatCreationForm(forms.Form):
    CHAT_TYPES = (
        ("individual", "Individual"),
        ("group", "Group"),
    )
    chat_type = forms.ChoiceField(
        choices=CHAT_TYPES,
        widget=forms.RadioSelect,
        label="Chat Type"
    )
    chat_name = forms.CharField(
        max_length=100,
        required=False,
        label="Group Chat Name",
        widget=forms.TextInput(attrs={
            "placeholder": "Enter group chat name (required if group chat)"
        }),
        help_text="Required if creating a group chat."
    )
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Select Users",
        help_text="Select one or more users for the chat"
    )

    def clean(self):
        cleaned_data = super().clean()
        chat_type = cleaned_data.get("chat_type")
        chat_name = cleaned_data.get("chat_name")
        users = cleaned_data.get("users")

        if chat_type == "group":
            if not chat_name:
                self.add_error("chat_name", "Group chats must have a chat name.")
            if users and users.count() < 2:
                self.add_error("users", "Group chats must include at least two users.")
        elif chat_type == "individual":
            if users and users.count() != 1:
                self.add_error("users", "Individual chats must include exactly one user.")

        return cleaned_data

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add consistent styling classes for inputs
        for field_name in ['username', 'email', 'password1', 'password2']:
            self.fields[field_name].widget.attrs.update({'class': 'input-field'})
