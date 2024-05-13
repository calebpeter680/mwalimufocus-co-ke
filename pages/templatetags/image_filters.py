from django import template

register = template.Library()

@register.filter
def remove_query_params(url):
    return url.split('?')[0]
