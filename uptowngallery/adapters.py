# adapters.py
from allauth.account.adapter import DefaultAccountAdapter
from .forms import CustomSignupForm  # Import Ir custom form


class CustomAccountAdapter(DefaultAccountAdapter):
    def get_signup_form(self, request):
        return CustomSignupForm  # Provide Ir custom signup form

    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit=False)
        user.save()

        # Add the name and shipping address to the user's profile
        name = form.cleaned_data.get("name")
        shipping_address = form.cleaned_data.get("shipping_address")
        user.profile.name = name
        user.profile.shipping_address = shipping_address
        user.profile.save()

        return user
