from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
def index(l, i): #method to index into list
    return l[i]