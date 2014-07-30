from django import template

register = template.Library()


@register.filter
def field_name(field):
    return field.field.widget.__class__.__name__
