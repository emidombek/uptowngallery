# signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from allauth.account.signals import user_signed_up
from django.contrib.auth import get_user_model
from uptowngallery.models import UserProfile

User = get_user_model()


def create_or_update_user_profile(sender, instance, created, **kwargs):
    try:
        if created:
            print("User created")
            UserProfile.objects.create(user=instance)
        else:
            print("User updated")
            instance.profile.save()
    except Exception as e:
        print(f"Error in create_or_update_user_profile: {e}")
