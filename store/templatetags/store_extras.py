from django import template
from django.conf import settings

register = template.Library()


@register.filter(name='currency')
def currency(value):
    """Format a number as store currency, e.g. 28500 -> "₦28,500"."""
    if value is None:
        value = 0
    try:
        value = float(value)
    except (TypeError, ValueError):
        return value

    symbol = getattr(settings, 'STORE_CURRENCY_SYMBOL', '$')
    if value == int(value):
        formatted = '{:,.0f}'.format(value)
    else:
        formatted = '{:,.2f}'.format(value)
    return f'{symbol}{formatted}'


@register.filter(name='get_item')
def get_item(dictionary, key):
    """Look up a dict value by a dynamic key inside a template, e.g.
    {{ my_dict|get_item:some_var }} — Django templates can't do my_dict[key] directly."""
    if not dictionary:
        return None
    return dictionary.get(key)





#from django import template
from django.contrib.auth.models import User

register = template.Library()



@register.filter(name='get_customer_profile')
def get_customer_profile(email):
    """
    Safely resolves profile relationships from a string email parameter 
    to extract billing structural fields across layout boundaries.
    """
    if not email:
        return None
    try:
        user = User.objects.get(email__iexact=email)
        # Tries the standard related_name configurations mapping back to User
        profile = getattr(user, 'profile', getattr(user, 'customer_profile', None))
        return profile
    except Exception:
        return None
