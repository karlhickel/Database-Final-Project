from django import template

register = template.Library()

@register.filter
def index(d, key):
    return d[key]
