from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key."""
    try:
        return dictionary.get(key)
    except AttributeError:
        return None

@register.filter
def mul(value, arg):
    """Multiply the arg and the value."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def make_list(value):
    """Convert comma-separated string to list."""
    if isinstance(value, str):
        return value.split(',')
    return value

@register.filter
def unique(value):
    """Return unique items from a list while preserving order."""
    if not value:
        return value
    seen = set()
    result = []
    for item in value:
        if item and item.strip() and item not in seen:
            seen.add(item)
            result.append(item)
    return result