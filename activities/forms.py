# New addition/changes: students/forms_auth.py
# (you can also put this in forms.py if you want, but I’m keeping it clean/separate)
# This form will power your sign-up page.

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

# 	UserCreationForm is a built-in Django form that already does password validation.
# 	We’re extending it to include email.
class CreateUser(UserCreationForm):
    """
    This form creates a new Django user (NOT a Student row).
    Fields:
    - username
    - password1
    - password2 (confirm password)
    We’re also adding email to store contact info.
    """

    email = forms.EmailField(
        required=True,
        help_text="We'll use this email if we need to contact you."
    )

    class Meta:

        # This is a pre-existing table in Django where we are already storing our internal user's data
        model = User
        fields = ["username", "email", "password1", "password2"]