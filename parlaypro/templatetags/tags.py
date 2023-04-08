from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
def index(l, i): #method to index into list
    return l[i]

#register custom filter
@register.filter
def get_item(dictionary, key): #method to index into dict
    return dictionary.get(key)