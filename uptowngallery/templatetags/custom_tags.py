from django import template
from allauth.account import messages as allauth_messages
from allauth.account.messages import messages as allauth_messages

register = template.Library()


@register.simple_tag
def render_allauth_messages():
    return allauth_messages.get_messages()
