from django.conf import settings
from .models import Category


def store_globals(request):
    """
    Makes the category list and currency symbol available in every template
    without each view having to pass them explicitly.
    """
    return {
        'nav_categories': Category.objects.all().order_by('name'),
        'currency_symbol': getattr(settings, 'STORE_CURRENCY_SYMBOL', '$'),
    }
