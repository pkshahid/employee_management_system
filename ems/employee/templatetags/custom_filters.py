from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    get a value from a dictionary using a dynamic key.
    Example: {{ my_dict|get_item:"keyname" }}
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None